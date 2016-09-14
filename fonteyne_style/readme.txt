1. Store files correctly:
 
CSS and JS files should be reside under 'static' directory in the module(the rest of subdirectory tree under 'static' is an optional convention):

    static/src/css/your_file.css
    static/src/js/your_file.js

2. Add files in XML(v8.0)

    Odoo v8.0 way is to add corresponding record in the XML:
        ​Add XML to the manifest (__openerp__.py):
        ...
        'data': [ 'your_file.xml'],
        ​...
        Then add following record in 'your_file.xml':
        <openerp>
            <data>
                <template id="assets_backend" name="your_module_name assets" inherit_id="web.assets_backend">
                    <xpath expr="." position="inside">
                        <link rel='stylesheet' href="/your_module_name/static/src/css/your_file.css"/>
                        <script type="text/javascript" src="/your_module_name/static/src/js/your_file.js"></script>
                    </xpath>
                </template>
            ....
            ....
            </data>
         </openerp>

