odoo.define('account_dynamic_reports_dev.tb', function(require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var session = require('web.session');
    var field_utils = require('web.field_utils');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    const { loadBundle } = require("@web/core/assets");
    var currency;
    var DynamicTbMain = AbstractAction.extend({
        template:'DynamicTbMain',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #pdf': 'print_pdf',
            'click #xlsx': 'print_xlsx',
            'click .view-source': 'view_gl',
        },
        init : function(view, code){
            this._super(view, code);
            this.wizard_id = code.context.wizard_id | null;
            this.session = session;
        },
        start : function(){
            var self = this;
            self.initial_render = true;
            if(! self.wizard_id){
                self._rpc({
                model: 'ins.trial.balance',
                method: 'create',
                args: [{res_model: this.res_model}]
                }).then(function (record) {
                    self.wizard_id = record;
                    self.plot_data(self.initial_render);
                })
            }else{
                self.plot_data(self.initial_render);
            }
        },
        print_pdf : function(e){
            e.preventDefault();
            var self = this;
            self._rpc({
            model: 'ins.trial.balance',
            method: 'get_report_datas',
            args: [[self.wizard_id]]
            }).then(function(data){
                var action = {
                        'type': 'ir.actions.report',
                        'report_type': 'qweb-pdf',
                        'report_name': 'account_dynamic_reports_dev.trial_balance',
                        'report_file': 'account_dynamic_reports_dev.trial_balance',
                        'data': {'js_data':data},
                        'context': {'active_model':'ins.trial.balance',
                            'landscape':1,
                            'from_js': true
                        },
                    'display_name': 'General Ledger',
                };
                return self.do_action(action);
            });
        },
        print_xlsx : function(){
            var self = this;
            self._rpc({
                model: 'ins.trial.balance',
                method: 'action_xlsx',
                args: [[self.wizard_id]],
            }).then(function(action){
                return self.do_action(action);
            });
        },
        formatWithSign : function(amount, formatOptions, sign){
            var currency_id = formatOptions.currency_id;
            currency_id = session.get_currency(currency_id);
            var without_sign = field_utils.format.monetary(Math.abs(amount), {}, formatOptions);
            if(!amount){return '-'};
            if (currency_id.position === "after") {
                return sign + '&nbsp;' + without_sign + '&nbsp;' + currency_id.symbol;
            } else {
                return currency_id.symbol + '&nbsp;' + sign + '&nbsp;' + without_sign;
            }
            return without_sign;
        },
        plot_data : function(initial_render = true){
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
            model: 'ins.trial.balance',
            method: 'get_report_datas',
            args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0];
                self.account_data = datas[1];
                self.retained = datas[2];
                self.subtotal = datas[3];
                _.each(self.account_data, function (k, v){
                    var formatOptions = {
                    currency_id: k.company_currency_id,
                    noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.retained, function (k, v){
                    var formatOptions = {
                    currency_id: k.company_currency_id,
                    noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.subtotal, function (k, v){
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                self.filter_data.date_from_tmp = self.filter_data.date_from;
                self.filter_data.date_to_tmp = self.filter_data.date_to;
                self.filter_data.date_from = field_utils.format.date(field_utils.parse.date(self.filter_data.date_from, {}, {isUTC: true}));
                self.filter_data.date_to = field_utils.format.date(field_utils.parse.date(self.filter_data.date_to, {}, {isUTC: true}));
                if(initial_render){
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionTb', {
                        filter_data : self.filter_data,
                    }));
                    self.$el.find('#date_from').datepicker({ dateFormat: 'dd-mm-yy' });
                    self.$el.find('#date_to').datepicker({ dateFormat: 'dd-mm-yy' });
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder:'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder:'Extra Options...',
                    }).val('bal_not_zero').trigger('change');
                    self.$el.find('.analytic-multiple').select2({
                        placeholder:'Select Analytic...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder:'Select Journal...',
                    });
                    self.$el.find('.account-multiple').select2({
                        placeholder:'Select Account...',
                    });
                }
                self.$('.py-data-container').html(QWeb.render('DataSectionTb', {
                    account_data : self.account_data,
                    retained : self.retained,
                    subtotal : self.subtotal,
                    filter_data : self.filter_data,
                }));
            });
        },
        view_gl : function(event){
            event.preventDefault();
            var self = this;
            var domains = {account_ids : [$(event.currentTarget).data('account-id')],
            initial_balance : false}
            var context = {};

            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i=0; i < journal_list.length; i++){
                journal_ids.push(parseInt(journal_list[i].id))
            }
            domains.journal_ids = journal_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i=0; i < account_list.length; i++){
                account_ids.push(parseInt(account_list[i].id))
            }
            domains.account_ids = account_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i=0; i < analytic_list.length; i++){
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            domains.analytic_ids = analytic_ids
            if($(".date_filter-multiple").select2('data').length === 1){
                domains.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            if ($("#date_from").val()){
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                domains.date_from = dateString;
            }
            if ($("#date_to").val()){
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                domains.date_to = dateString;
            }
            if(!domains.date_from && !domains.date_to && !domains.date_range){domains.date_from = self.filter_data.date_from_tmp;
            domains.date_to = self.filter_data.date_to_tmp;}
            var gl_wizard_id = 0;
            self._rpc({
                model: 'ins.general.ledger',
                method: 'create',
                args: [{}]
                }).then(function (record){
                    gl_wizard_id = record;
                    self._rpc({
                        model: 'ins.general.ledger',
                        method: 'write',
                        args: [gl_wizard_id, domains]
                    }).then(function () {
                        var action = {
                            type: 'ir.actions.client',
                            name: 'GL View',
                            tag: 'dynamic_gl',
                            nodestroy: true ,
                            target: 'new',
                            context: {
                                wizard_id:gl_wizard_id,
                                active_id: self.wizard_id,
                                active_model:'ins.trial.balance'
                            }
                        }
                        return self.do_action(action);
                    })
                })
        },
        update_with_filter : function(event){
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range:false};
            output.display_accounts = 'all';
            output.show_hierarchy = false;

            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i=0; i < journal_list.length; i++){
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i=0; i < account_list.length; i++){
                account_ids.push(parseInt(account_list[i].id))
            }
            output.account_ids = account_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i=0; i < analytic_list.length; i++){
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            output.analytic_ids = analytic_ids
            if($(".date_filter-multiple").select2('data').length === 1){
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            var options_list = $(".extra-multiple").select2('data')
            for (var i=0; i < options_list.length; i++){
                if(options_list[i].id === 'bal_not_zero'){
                    output.display_accounts = 'balance_not_zero';
                }
                if(options_list[i].id === 'show_hierarchy'){
                    output.show_hierarchy = true;
                }
            }
            if ($("#date_from").val()){
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
            }
            if ($("#date_to").val()){
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            self._rpc({
                model: 'ins.trial.balance',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function(res){
                self.plot_data(self.initial_render);
            });
        },
    });

    core.action_registry.add('dynamic_tb', DynamicTbMain);

return DynamicTbMain;

});