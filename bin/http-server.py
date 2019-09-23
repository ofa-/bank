#!/usr/bin/python
# encoding: UTF-8

import http.server as BaseHTTPServer
import cgi
import os

def required_files():
        check_file("../bin/download.sh")
        check_file("../etc/categories.html")
        check_file("../etc/config.txt")

class PostHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_POST(self):
        #self.echo_form_fields()
        self.save_fields(account=self.path)
        self.build_main_page()

    def do_GET(self):

        patch_wfile_write(self)

        if (self.path == "/"):
                self.build_main_page()

        elif self.path == "/favicon.ico":
                pass
        elif self.path.startswith("/exit"):
                os.system("killall chrome")
                os.system("killall http-server.py")

        elif self.path.startswith("/download-all"):
                self.download(download_buttons["download-all"])

        elif self.path.startswith("/download"):
                self.download(download_buttons["download"])

        elif self.path.startswith("/search"):
                self.build_search_page()

        elif self.path.startswith("/data/"):
                account = self.path.split('/data/')[1].replace('?','')
                self.send_account_data(account)

        elif self.path.startswith("/view/"):
                account = self.path.split('/view/')[1].replace('?','')
                if account in grouped_accounts:
                        self.make_grouped_account_csv(account, grouped_accounts[account].split(" "))
                self.build_stats_page(account)

        elif self.path.startswith("/edit/"):
                account = self.path.split('/edit/')[1].replace('?','')
                if account in grouped_accounts:
                        self.build_main_page()
                        return
                self.build_account_page(account)

        else:
                self.build_main_page()


    def download(self, args):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=UTF-8")
        self.end_headers()
        self.wfile.write("  D o w n l o a d i n g  ".center(80, "="))
        self.wfile.write("\n" * 2)
        cmd = "../bin/download.sh " + args
        f = os.popen(cmd)
        c = f.read(1)
        while c:
                self.wfile.write(c)
                self.wfile.flush()
                c = f.read(1)
        f.close()
        self.wfile.write("\n" + "  D o n e  ".center(80, "=") + "\n")


    def make_grouped_account_csv(self, account, members):
        out = open(account + ".csv", "w")
        for f in members:
                out.write(open(f + ".csv").read())
        out.close()


    def build_account_page(self, account):
        self.emit_html_head(title=account)
        self.emit_javascript()
        self.emit_style()
        self.build_input_form(account)
        self.emit_categories_box()
        self.emit_html_tail()


    def build_main_page(self):
        self.emit_html_head(title="accounts")
        self.wfile.write('<form method="GET">\n');

        files = filter(lambda x: x.endswith(".csv"), os.listdir("."))
        accounts = [f.replace('.csv', '') for f in files]
        accounts = list(set(accounts + list(grouped_accounts.keys())))
        accounts.sort()

        self.wfile.write("""
                <hr>
                <tt>E D I T</tt>
                <hr>
        """)

        for account in accounts:
                if account in grouped_accounts:
                        continue
                self.wfile.write("""
                <input type="submit" value="%s" onclick="this.form.action='/edit/%s';">
                        """ % (account, account));

        self.wfile.write("""
                <hr>
                <tt>V I E W</tt>
                <hr>
        """)

        for account in accounts:
                self.wfile.write("""
                <input type="submit" value="%s" onclick="this.form.action='/view/%s';">
                        """ % (account, account));

        self.wfile.write("""
                <hr>
                <hr>
<!--
                <input type="submit" value="EXIT" onclick="this.form.action='/exit';">
-->
                <input type="submit" value="DOWNLOAD" onclick="this.form.action='/download';">
                <input type="submit" value="DOWNLOAD ALL" onclick="this.form.action='/download-all';">
                <input type="submit" value="SEARCH" onclick="this.form.action='/search';">
        """)

        self.wfile.write('</form>\n');
        self.emit_html_tail()


    def build_search_page(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()
        files = filter(lambda x: x.endswith(".csv"), os.listdir("."))
        accounts = [f.replace('.csv', '') for f in files]
        pagetext = open("../bin/search.html").read();
        self.wfile.write(pagetext.replace("%%ACCOUNTS%%", str(accounts)))

    def send_account_data(self, account):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=UTF-8")
        self.end_headers()
        self.wfile.write(open(account).read())


    def build_stats_page(self, account):
        self.emit_html_head(title=account)
        self.emit_stats_style_and_script()

        (total, month, text) = self.compute_stats(account)

        categories = list(total.keys())
        categories.sort()
        months = list(month.keys())
        months.sort(reverse=True)

        self.wfile.write('<table>\n')
        self.wfile.write("""<tr><th valign="top" onclick=toggle_sub_categories(this)>Catégorie<br><br><div style="text-align: right">E<br>D<br>R</div><div style="text-align: left">[+]</div></th>\n""")

        # compute yearly totals ops/minus/plus/savings based on monthly totals
        tot = [0, 0, 0, 0]
        for m in months:
                tot = map(sum, zip(tot, month[m]))
        (ops, minus, plus, savings) = tot
        balance = savings + minus + plus
        income = 0
        for cat in income_categories:
                if cat in total:
                        income += self.get_income(months, total[cat])
        spendings = minus + plus - income
        # display yearly totals
        self.wfile.write("""<th class="tot" valign="top">Total<br>Période<div style="text-align: right">%+.0f<br>%+.0f<br><u>%+.0f</u><br>%+.0f</div></th>\n""" % (savings, spendings, income, balance) )
        # display monthly totals
        for m in months:
                (ops, minus, plus, savings) = month[m]
                self.wfile.write("""<th>%s<br>%s ops<div style="text-align: right">%+.0f<br>%+.0f<br><u>%+.0f</u><br>%+.0f</div></th>\n""" % (m, ops, savings, minus, plus, savings + minus + plus ) )
        self.wfile.write("""</tr>\n""")

        main_cat = self.get_main_categories(categories, total, months, text)

        # display categories totals
        main_cat_name  = categories[0].split('>')[0].strip()
        for c in categories:
                main_cat_curr = c.split('>')[0].strip()
                if main_cat_name != main_cat_curr:
                        (main_total, main_text) = main_cat[main_cat_name]
                        self.emit_main_category_line(main_cat_name, main_total, main_text)
                        main_cat_name = main_cat_curr
                self.emit_category_line(c, months, total, text)
        # emit last main category line
        (main_total, main_text) = main_cat[main_cat_name]
        self.emit_main_category_line(main_cat_name, main_total, main_text)

        # compute monthly account balance
        months.sort()
        balance = {}
        curr = self.get_previous_balance(account)
        for m in months:
                curr +=  month[m][1] + month[m][2] + month[m][3]
                balance[m] = curr
        # display account balance
        self.wfile.write("""<tr><th colspan=2>Solde Compte</th>\n""")
        months.sort(reverse=True)
        for m in months:
                self.wfile.write("""<th>%.2f€</th>\n""" % balance[m] )

        self.wfile.write('</tr>\n')
        self.wfile.write('</table>\n');

        self.emit_html_tail()


    def emit_category_line(self, category, months, total, text):
        self.wfile.write("""<tr class="c"><th>%s</th>\n""" % category)
        yearly_tot = 0
        for m in months:
                if m in total[category]:
                        yearly_tot += total[category][m]
        self.wfile.write('<td class="tot">%s</td>\n' % ("%+.0f" % yearly_tot) )

        for m in months:
                if m in total[category]:
                        amount = "%+.2f" % total[category][m]
                        detail = "<pre class='det'>\n%s</pre>" % text[category][m]
                        js = 'onmouseover="show(this)" onmouseout="hide(this)"'
                else:
                        amount = detail = js = ""
                self.wfile.write('<td %s>%s%s</td>\n' % (js, amount, detail) )
        self.wfile.write('</tr>\n')


    def emit_main_category_line(self, name, total, text):
        self.wfile.write("""<tr><td class="mch">%s</td>\n""" % name)
        yearly_tot = 0
        for i in range(len(total)):
                if total[i]:
                        yearly_tot += total[i]
        self.wfile.write('<td class="tot">%s</td>\n' % ("%+.0f" % yearly_tot) )
        for i in range(len(total)):
                if total[i]:
                        amount = "%+.0f" % total[i]
                        detail = "<pre class='det'>\n%s</pre>" % text[i]
                        js = 'onmouseover="show(this)" onmouseout="hide(this)"'
                else:
                        amount = detail = js = ""
                self.wfile.write('<td class="mc" %s>%s%s</td>\n' % (js, amount, detail) )
        self.wfile.write('</tr>\n')


    def get_previous_balance(self, account):
        ret = 0
        tag = "SOLDE PRECEDENT";
        csv = open('./%s.csv' % account)
        lines = csv.readlines()
        for line in lines:
                if line[0:len(tag)] != tag:
                        continue
                ret += float(line.split(' ')[-1].replace(',','.'))
        return ret


    def get_income(self, months, income_category_total):
        income = 0
        for m in months:
                if m in income_category_total:
                        income += income_category_total[m]
        return income


    def compute_stats(self, account):
        total = {}
        month = {}
        text  = {}
        anti_alias = {}

        csv = open('./%s.csv' % account)
        lines = csv.readlines()
        for line in lines:
                fields = line.split(';')
                if not is_date(fields[0]):
                        continue
                date_str = fields[0]
                category = fields[6].strip()
                amount   = float((fields[3]+fields[4]).replace(',','.'))
                date     = date_str.split('/')
                yy_mm = "20%s-%s" % ( date[2], date[1] )
                if not yy_mm in month:
                        month[yy_mm] = [ 0, 0, 0, 0 ]
                if category in savings_categories:
                        i = 3
                else:
                        if amount > 0:
                                i = 2
                        else:
                                i = 1
                month[yy_mm][i] += amount  # monthly totals for + or - or savings, separated
                month[yy_mm][0] += 1       # monthly nb of operations

                if not date_str in anti_alias:
                        anti_alias[date_str] = [ amount ]
                else:
                        if -amount in anti_alias[date_str]:  # cross-account transfer aliases
                                if i < 3:
                                        month[yy_mm][i]   -= amount
                                        month[yy_mm][3-i] += amount
                                anti_alias[date_str].remove(-amount)
                        else:
                                anti_alias[date_str] += [ amount ]


                if category in total:
                        if yy_mm in total[category]:
                                total[category][yy_mm] += amount
                                text [category][yy_mm] += make_detail_line(fields)
                        else:
                                total[category][yy_mm] = amount
                                text [category][yy_mm] = make_detail_line(fields)
                else:
                        total[category] = { yy_mm : amount }
                        text [category] = { yy_mm : make_detail_line(fields) }

        return (total, month, text)

    def get_main_categories(self, categories, total, months, text):
        # compute main categories totals and text lines
        main_cat = {}
        main_cat_name  = None
        for c in categories:
                main_cat_curr = c.split('>')[0].strip()
                if main_cat_name != main_cat_curr:
                        if main_cat_name:
                                main_cat[main_cat_name] = (main_cat_total, main_cat_text)
                        main_cat_name = main_cat_curr
                        main_cat_total = [0]  * len(months)
                        main_cat_text  = [""] * len(months)
                for (m, i) in zip(months, range(len(months))):
                        if m in total[c]:
                                main_cat_total[i] += total[c][m]
                                main_cat_text[i] += str(text[c][m])
        main_cat[main_cat_name] = (main_cat_total, main_cat_text)

        return main_cat


    def emit_stats_style_and_script(self):
        self.wfile.write("""
                <style>
                        /* yearly totals */
                        .tot { /* font-size: 0px; */ }

                        /* overall */
                        td,th { font-family: monospace; text-align:right; }
                        th    { text-align: center; background-color: #6868FF; }
                        th    { border: 1px solid black; }

                        /* sub-categories lines */
                        tr.c    { display: none; }
                        tr.c th { text-align: left;   background-color: #E0E0E0; }
                        .det    { position: absolute; display: none; background-color: #69FF69; z-index: 1; }

                        /* main categories lines */
                        td.mch { }
                        td.mc  { background-color: #E0E0E0; }

                        /* categories toggle button */
                        th   { position: relative; }
                        th a { position: absolute; bottom: 0; right: 0; text-decoration: none; }
                </style>
                <script>
                        function getLeft(o) {
                                var ret = 0;
                                while (o != null) {
                                        ret += o.offsetLeft;
                                        o = o.offsetParent;
                                }
                                return ret;
                        }
                        function show(o) {
                                var detailElt = o.firstChild.nextSibling;
                                detailElt.style.left = getLeft(o) + 20;
                                detailElt.style.display='inline';

                                var x = getLeft(detailElt);
                                if (x + detailElt.offsetWidth > document.body.offsetWidth + document.body.scrollLeft) {
                                        detailElt.style.left =  o.offsetLeft + document.body.offsetWidth + document.body.scrollLeft - (x + detailElt.offsetWidth);
                                }
                        }
                        function hide(o) {
                                var detailElt = o.firstChild.nextSibling;
                                detailElt.style.display='none';
                        }
                        function toggle_sub_categories(obj) {
                                obj.disp = ! obj.disp;
                                var elts = document.getElementsByClassName("c");
                                for (i=0; i < elts.length; i++) {
                                        elts[i].style.display = (obj.disp ? "table-row" : "none");
                                }
                                obj.lastChild.innerHTML = (obj.disp ? "[-]" : "[+]");
                        }
                </script>
        """)


    def echo_form_fields(self):

        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s (%d bytes)\n' % (field,
                                                                 file_len))
            else:
                # Regular form value
                self.wfile.write('\t%s=%s\n' % (field, form[field].value))
        return


    def save_fields(self, account):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        csv = open('./%s.csv' % account)
        out = open('./%s.csv.new' % account, 'w')
        i = 1
        lines = csv.readlines()
        for line in lines:
                fields = line.split(';')
                if not is_date(fields[0]):
                        out.write(line)
                        continue
                has_amount = form.has_key("amount.%i" % i)
                if not has_amount:
                        desc_string = form["desc.%i" % i].value
                        cat_string  = form["cat.%i"  % i].value
                        self.update_line_fields(fields, desc_string, cat_string)
                        out.write(";".join(fields))
                        out.write('\n')
                        i += 1
                        continue
                while has_amount:
                        desc_string = form["desc.%i" % i].value
                        cat_string  = form["cat.%i"  % i].value
                        amount      = form["amount.%i" % i].value
                        if float(amount):
                                self.update_line_fields(fields, desc_string, cat_string, amount)
                                out.write(";".join(fields))
                                out.write('\n')
                        i += 1
                        has_amount = form.has_key("amount.%i" % i)

        out.close()
        os.rename('./%s.csv.new' % account, './%s.csv' % account)


    def update_line_fields(self, fields, description, category, amount=None):
        fields[2] = description.replace(";", " ")        # zap ';'s in description field
        fields[5] = ""                                        # zero-out original comment field (merged with desc in js)
        if amount:
                fields[4] = amount
        if len(fields) == 8:
                fields.pop()
        if category[-1] == "*":
                fields[6] = category[:-1]
                fields.append("*")
        else:
                fields[6] = category


    def build_input_form(self, account):
        self.wfile.write("""
        <form        id="input" method="POST" action="/%s">
                <input type="button" value="SAVE" onclick="submitForm(this.form)">
        """ % account
        )

        csv = open('./%s.csv' % account)
        lines = csv.readlines()
        for line in lines:
                fields = line.split(';')
                if not is_date(fields[0]):
                        continue
                category = fields[-1].strip()
                self.emit_transaction_line(fields)

        self.wfile.write("""
                <input type="button" value="SAVE" onclick="submitForm(this.form)">
        </form>
        """
        )


    def emit_categories_box(self):
        self.wfile.write("""
        <div id="menubox">
        """
        + open("../etc/categories.html").read() +
        """
        </div>
        """
        )

    def emit_transaction_line(self, field):
        date_str    = field[0]
        comment_str = field[2].strip()
        extra_info  = field[5].strip()
        amount_str  = "%s%s" % (field[3], field[4])
        category    = field[6].strip()
        to_check    = ""

        if extra_info[0:len(comment_str)] == comment_str:
                comment_str = extra_info
        if category == "":
                to_check = ' class="check"'
                category = "?"
        if len(field) == 8 :
                to_check = ' class="check"'

        self.wfile.write('<div>')
        self.wfile.write('<tt>%s</tt> ' % date_str)
        self.wfile.write('<input value="%s" size="40">' % comment_str)
        self.wfile.write('<tt id="s">::</tt>')
        self.wfile.write('<tt id="e">%s</tt>' % amount_str)
        self.wfile.write('<a%s>%s</a>' % (to_check, category))
        self.wfile.write('</div>\n')

    def emit_html_head(self, title="accounts"):
        self.send_response(200);
        #self.send_header("Content-type", "text/html")
        #self.end_headers()
        self.wfile.write("""
        <html>
        <head>
                <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
                <meta name="viewport" content="initial-scale=1.0,maximum-scale=1.0" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <title>%s</title>
        </head>

        <body>
        """ % (title)
        )

    def emit_html_tail(self):
        self.wfile.write("""
        </body>
        </html>
        """
        )


    def emit_style(self):
        self.wfile.write("""
        <style>
        form tt#e { position: absolute; width:  6em; padding-top: .5em; text-align:right; }
        form a    { position: absolute; width: 20em; padding-top: .5em; margin-left: 7em; }
        form a    { font-family: monospace; text-decoration: none; color: inherit; }
        a.check   { text-decoration: underline; color: blue; }
        input.amt { text-align: right; width: 5.4em; }
        #menubox  {         position: absolute; display: none;
                        border: solid 1px orange; background: #20E0E0;
                        cursor: default; width:33em; font-family: monospace;
                }
        #menubox a { cursor: pointer; }
        form tt#s { cursor: pointer; }
        </style>
        """
        )

    def emit_javascript(self):
        self.wfile.write("""
<script>

var curObj = null;
function do_menu(obj) {
        var box = document.getElementById("menubox");
        box.style.top  = getY(obj);
        box.style.left = getX(obj) + 100;
        box.style.display = "block";

        if (curObj)
                curObj.style.border = "";
        curObj = obj;
        curObj.style.border = "1px dashed orange";
        curObj.curCat = null;
}

function hide_menu() {
        document.getElementById("menubox").style.display = "none";
        if (curObj)
                curObj.style.border = "";
        curObj = null;
}

function select(obj) {
        var category = obj.parentNode.firstChild;
        var value;
        if (obj == category) {
                value = category.firstChild.nodeValue;
        }
        else {
                value = category.firstChild.nodeValue + " > " + obj.firstChild.nodeValue;
        }
        curObj.firstChild.nodeValue = value;
        curObj.focus();
        setNotActive(curObj);
        hide_menu();
}

function setOnClickHandlers(body, menubox) {
        var links = getDescendantsByTagName(document.getElementById(menubox), "a");
        for (i in links) {
                links[i].onclick = function () { select(this); }
                links[i].onmouseover = function () { this.style.border = "1px solid black"; }
                links[i].onmouseout  = function () { this.style.border = ""; }
        }
        body.onclick = hide_menu;
        document.getElementById(menubox).onclick = hide_menu;
}

function setOnMouseOverHandlers(body, inputForm) {
        if (is_touch_device())
                setActive = function(o) { o.className   = "check"; }

        var links = getDescendantsByTagName(document.getElementById(inputForm), "a");
        for (i in links) {
                l = links[i];
                initCategoryLink(l);
        }
}

function initCategoryLink(l) {
        l.setAttribute("href", "javascript:");
        if (l.className == "check") {
                setActive(l);
        }
        l.onclick = function (e) {
                e.stopPropagation();
                if (this.className == "check") {
                        setNotActive(this);
                        hide_menu();
                }
                else {
                        setActive(this);
                        do_menu(this);
                }
        }
}

function setActive(o) {
        o.className   = "check";
        o.onmouseover = function (e) { do_menu(this); }
        o.onkeypress  = function (e) { handle_key(curObj, e.keyCode); }
        o.blur();
}

function setNotActive(o) {
        o.className = "";
        o.onmouseover = o.onkeypress = null;
        o.blur();
}

function handle_key(obj, keyCode) {
        var input = keyCode - 48;
        if (input < 0 || input > 9)
                return;

        var cat = getDescendantsByTagName(document.getElementById("menubox"), "li");
        if (obj.curCat == null) {
                if (input == 0 || input > cat.length)
                        return;
                obj.curCat = cat[input-1].firstChild;
                obj.firstChild.nodeValue = obj.curCat.firstChild.nodeValue;
                return;
        }

        var opt = getDescendantsByTagName(obj.curCat.parentNode, "a");
        if (input == 0 || input+1 > opt.length)
                select(obj.curCat);
        else
                select(opt[input]);

        obj.curCat = null;
}

function convertCategoriesToInputs(inputForm) {
        var links = getDescendantsByTagName(inputForm, "a");
        var nb=1;
        for (i in links) {
                var l = links[i];
                var v = l.firstChild.nodeValue;
                if (l.className == "check")
                        v += "*";
                createHiddenInput(inputForm, "cat." + nb, v);
                nb = nb + 1;
        }
}

function setNamesOnTextInputs(inputForm) {
        var inputs = getDescendantsByTagName(inputForm, "input");
        var nb=1;
        for (i in inputs) {
                var input = inputs[i];
                if (input.type != "text")
                        continue;
                if (input.className == "amt") {
                        createHiddenInput(inputForm, "amount." + (nb-1), input.value);
                }
                else {
                        input.setAttribute("name",  "desc." + nb);
                        nb = nb + 1;
                }
        }
}

function createHiddenInput(inputForm, name, value) {
        var input = document.createElement("input");
        input.setAttribute("type", "hidden");
        input.setAttribute("name",  name);
        input.setAttribute("value", value);
        inputForm.appendChild(input);
}

function submitForm(form) {
        setNamesOnTextInputs(form);
        convertCategoriesToInputs(form);
        form.submit();
}

function updateValue(input) {
        var linked = input.linked;
        var inputVal = parseFloat(input.value || "0");
        var linkedVal = parseFloat(linked.value);
        var prevVal = parseFloat(input.prev) || 0;
        if (isNaN(inputVal)) inputVal = prevVal;
        if (linkedVal * inputVal < 0 && !input.value[0].match(/[+-]/))
                inputVal = - inputVal;
        if (linkedVal * (linkedVal + prevVal - inputVal) <= 0)
                inputVal = prevVal;
        linked.value = (linkedVal + prevVal - inputVal).toFixed(2);
        linked.prev = linked.value;
        input.value = inputVal.toFixed(2);
        input.prev = input.value;
}

function splitLine(ev) {
        var line = ev.target.parentNode;
        var newLine = document.createElement("div");
        newLine.innerHTML = line.innerHTML;
        var amountElt = newLine.getElementsByTagName("tt")[2];
        var input = createAmountInput(amountElt, "0.00");
        input.onchange = function() { updateValue(this) };
        initCategoryLink(newLine.getElementsByTagName("a")[0]);
        line.parentNode.insertBefore(newLine, line.nextSibling);
        amountElt = line.getElementsByTagName("tt")[2];
        if (!amountElt.firstChild.type) {
                var dinput = createAmountInput(amountElt, amountElt.innerHTML);
                dinput.setAttribute("disabled", "1");
        }
        input.linked = amountElt.firstChild;
        input.onfocus = function(e) { this.select(); }
        input.onmouseup = function(e) { return false; }
        input.focus();
}

function createAmountInput(amountElt, value) {
        amountElt.innerHTML = "<input class='amt'>";
        amountElt.firstChild.value = value;
        amountElt.style.paddingTop = 0;
        return amountElt.firstChild;
}

function setSplittersOnClick() {
        var inputs = document.getElementsByTagName('input');
        for (var i=0; i < inputs.length; i++) {
                var splitter = input[i].nextSibling;
                splitter.onclick = splitLine;
        }
}



// 2 funcs below courtesy of "some user in a forum"

function getX( oElement )
{
        var iReturnValue = 0;
        while( oElement != null ) {
                iReturnValue += oElement.offsetLeft;
                oElement = oElement.offsetParent;
        }
        return iReturnValue;
}

function getY( oElement )
{
        var iReturnValue = 0;
        while( oElement != null ) {
                iReturnValue += oElement.offsetTop;
                oElement = oElement.offsetParent;
        }
        return iReturnValue;
}


// 2 funcs below courtesy of http://snipplr.com/view/8212/dom-traversal/

function getChildElements(obj) {
        var children = obj.childNodes;
        var elems = [];
        if(children) {
                for(var i=0; i<children.length; i++) {
                        if(children[i].nodeType == document.ELEMENT_NODE) {
                                elems.push(children[i]);
                        }
                }
        }
        return elems;
}

function getDescendantsByTagName(obj, tagName, childrenOnly) {
        var results = [];
        if(!tagName)
                return results;
        tagName = tagName.toLowerCase();
        var elems = getChildElements(obj);
        for(var i=0; i<elems.length; i++) {
                if(elems[i].nodeName.toLowerCase() == tagName)
                        results.push(elems[i]);

                if(!childrenOnly) {
                        results = results.concat(getDescendantsByTagName(elems[i], tagName));
                }
        }
        return results;
}

// func below courtesy of http://stackoverflow.com/questions/4817029/#4819886

function is_touch_device() {
        return 'ontouchstart' in window // works on most browsers
                || 'onmsgesturechange' in window; // works on ie10
}

function setOnFocusForInputs() {
        var inputs = getDescendantsByTagName(document.body, "input");
        for (i in inputs) {
                o = inputs[i];
                if (o.type == "text") {
                        o.onfocus   = function () { this.select(); }
                        o.onmouseup = function () { return false;  }
                }
        }
}

onload = function() {
        setOnClickHandlers(document.body, 'menubox');
        setOnMouseOverHandlers(document.body, 'input');
        //setOnFocusForInputs();
        setSplittersOnClick();
}

</script>

        """
        )


def make_detail_line(fields):
        date=fields[0].strip()
        text=fields[2].strip()
        mony=(fields[3]+fields[4]).strip()
        if len(text) > 60:
                text = text[0:56] + "..."
        return ("%8s %-60s %9s\n" % (date, text, mony))


def patched_write(o, txt):
    if hasattr(txt, 'encode'):
        txt = txt.encode()
    o._orig_w(txt)

def patch_wfile_write(self):
    import types
    self.wfile._orig_w = self.wfile.write
    self.wfile.write = types.MethodType(patched_write, self.wfile)


#from datetime import strptime
from time import strptime
def is_date(str):
        try:
                strptime(str, '%d/%m/%y')
                return 1
        except:
                return 0

def check_file(f):
        if not os.path.exists(f):
                print "required file not found:", f
                exit(1)

def read_config():
        exec(open("../etc/config.txt").read(), globals())
        income_categories
        savings_categories
        grouped_accounts
        download_buttons

def run(handler_class):
        required_files()
        read_config()
        os.system("firefox http://localhost:1969 &")
        server_class=BaseHTTPServer.HTTPServer
        server_address = ('', 1969)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()


run(handler_class=PostHandler)

