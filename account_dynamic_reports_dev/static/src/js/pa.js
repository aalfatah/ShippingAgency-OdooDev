odoo.define('account_dynamic_reports_dev.pa', function(require) {
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
    var DynamicPaMain = AbstractAction.extend({
        template:'DynamicPaMain',
        events: {
                'click #filter_apply_button': 'update_with_filter',
                'click #group_by_partner': 'group_by_partner',
                'click #group_by_company': 'plot_data',
                'click #pdf': 'print_pdf',
                'click #xlsx': 'print_xlsx',
                'click .view-source': 'view_move_line',
                'click .py-mline': 'fetch_move_lines',
                'click .py-mline-page': 'fetch_move_lines_by_page',
                // 'click #as_on_date': 'preventDef',
                // 'click #bucket_1': 'preventDef',
                // 'click #bucket_2': 'preventDef',
                // 'click #bucket_3': 'preventDef',
                //'click #bucket_4': 'preventDef',
                //'click #bucket_5': 'preventDef',
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
                    model: 'ins.partner.ageing',
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
                model: 'ins.partner.ageing',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function(data){
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_name': 'account_dynamic_reports_dev.partner_ageing',
                    'report_file': 'account_dynamic_reports_dev.partner_ageing',
                    'data': {'js_data':data},
                    'context': {'active_model':'ins.partner.ageing',
                    'landscape':1,
                    'from_js': true
                },
                'display_name': 'Partner Ageing',
                };
                return self.do_action(action);
            });
        },

        print_xlsx : function(){
            var self = this;
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'action_xlsx_dev',
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
        formatWithNoSign : function(amount, formatOptions, sign){
            var currency_id = formatOptions.currency_id;
            currency_id = session.get_currency(currency_id);
            var without_sign = field_utils.format.monetary(Math.abs(amount), {}, formatOptions);
            if(!amount){return '-'};
            return sign + without_sign;
        },

        plot_data : function(initial_render = true){
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.ageing_data = datas[1]
                self.period_dict = datas[2]
                self.period_list = datas[3]
                self.sub_lines = datas[4]
                self.countMember     = ( _.size(datas[2]) )
                // self.percent_view = datas[6]
                _.each(self.ageing_data, function (k, v){
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    for(var z = 0; z < self.period_list.length; z++){
                        if(self.filter_data['display_currency']){
                            k[self.period_list[z]] = self.formatWithSign(k[self.period_list[z]], formatOptions, k[self.period_list[z]] < 0 ? '-' : '');
                        }else{
                            k[self.period_list[z]] = self.formatWithNoSign(k[self.period_list[z]], formatOptions, k[self.period_list[z]] < 0 ? '-' : '');
                        }
                    }
                    if(self.filter_data['display_currency']){
                        k.total   = self.formatWithSign(k.total, formatOptions,   k.total   < 0 ? '-' : '');
                    }else{
                        k.total   = self.formatWithNoSign(k.total, formatOptions,   k.total   < 0 ? '-' : '');
                    }
                });
                if(initial_render){
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPa', {
                        filter_data : self.filter_data,
                    }));
                    self.$el.find('#as_on_date').datepicker({ dateFormat: 'dd-mm-yy' });
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder:'Select Account Type...',
                    });
                    self.$el.find('.partner-type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder:'Select Partner Type...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder:'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder:'Select Tag...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder:'Extra Options...',
                    })
                    .val('include_details').trigger('change')
                    ;
                }
                self.$('.py-data-container-orig').html(QWeb.render('DataSectionPa', {
                    ageing_data : self.ageing_data,
                    period_dict : self.period_dict,
                    period_list : self.period_list,
                    filter_data : self.filter_data,
                    sub_lines : self.sub_lines,
                }));
                self.loader_enable_ui();
            });
        },
        plot_data_group_by_partner : function(initial_render = true){
            initial_render = true
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
                self._rpc({
                    model: 'ins.partner.ageing',
                    method: 'get_report_datas_group_by_partner',
                    args: [[self.wizard_id]],
                }).then(function (datas) {

                    self.filter_data = datas[0]
                    self.ageing_data = datas[1]
                    self.group_lines = datas[2]
                    self.period_list = datas[3]
                    self.sub_lines = datas[4]
                    // self.tot_partner_group = datas[5]
                    // self.partner_list = datas[6]

                    Object.keys(self.tot_partner_group).forEach(function(key) {
                        var value = self.tot_partner_group[key];

                        _.each(value, function (k, v){
                            var formatOptions = {
                                currency_id: k.company_currency_id,
                                noSymbol: true,
                            };
                            if(self.filter_data['display_currency']){
                                if(v == 'total'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == 'Current'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '1 - 30'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '31 - 60'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '61 - 90'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '90 +'){ k   = self.formatWithSign(k, formatOptions, k   < 0 ? '-' : '');}
                            }else{
                                if(v == 'total'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == 'Current'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '1 - 30'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '31 - 60'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '61 - 90'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                                if(v == '90 +'){ k   = self.formatWithNoSign(k, formatOptions, k   < 0 ? '-' : '');}
                            }
                        });

                    });


                    if(initial_render){
                            self.$('.py-control-panel').html(QWeb.render('FilterSectionPa', {
                            filter_data : self.filter_data,
                            sub_lines : self.sub_lines,
                            tot_partner_group : self.tot_partner_group,
                            partner_list : self.partner_list,
                            group_by_partner : true,

                        }));
                        self.$el.find('#as_on_date').datepicker({ dateFormat: 'dd-mm-yy' });
                        self.$el.find('.type-multiple').select2({
                            maximumSelectionSize: 1,
                            placeholder:'Select Account Type...',
                        });
                        self.$el.find('.partner-type-multiple').select2({
                            maximumSelectionSize: 1,
                            placeholder:'Select Partner Type...',
                        });
                        self.$el.find('.partner-multiple').select2({
                            placeholder:'Select Partner...',
                        });
                        self.$el.find('.partner-tag-multiple').select2({
                            placeholder:'Select Tag...',
                        });
                        self.$el.find('.extra-multiple').select2({
                            placeholder:'Extra Options...',
                        })
                        .val('include_details').trigger('change');
                    }
                    self.$('.py-data-container-orig').html(QWeb.render('DataSectionPa', {
                        ageing_data : self.ageing_data,
                        group_lines : self.group_lines,
                        period_list : self.period_list,
                        filter_data : self.filter_data,
                        sub_lines : self.sub_lines,
                        group_by_partner : true,
                        tot_partner_group : self.tot_partner_group,
                        partner_list : self.partner_list,
                        })
                    );
                    self.loader_enable_ui();
                });
        },
        ageing_lines_by_page : function(offset, account_id){
            var self = this;
            return self._rpc({
                model: 'ins.partner.ageing',
                method: 'process_detailed_data',
                args: [self.wizard_id, offset, account_id],
            })
        },
        fetch_move_lines_by_page : function(event){
            event.preventDefault();
            var self = this;
            var partner_id = $(event.currentTarget).data('partner-id');
            var offset = parseInt($(event.currentTarget).data('page-number')) - 1;
            var total_rows = parseInt($(event.currentTarget).data('count'));
            self.loader_disable_ui();
            self.ageing_lines_by_page(offset, partner_id).then(function(datas){
                var count = datas[0];
                var offset = datas[1];
                var account_data = datas[2];
                var period_list = datas[3];
                _.each(account_data, function (k, v){
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    if(self.filter_data['display_currency']){
                        k.range_0 = self.formatWithSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                        k.range_1 = self.formatWithSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                        k.range_2 = self.formatWithSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                        k.range_3 = self.formatWithSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                        k.range_6 = self.formatWithSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                    }else{
                        k.range_0 = self.formatWithNoSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                        k.range_1 = self.formatWithNoSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                        k.range_2 = self.formatWithNoSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                        k.range_3 = self.formatWithNoSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                        k.range_6 = self.formatWithNoSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                    }
                    k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
                });
                $(event.currentTarget).parent().parent().parent().find('.py-mline-table-div').remove();
                $(event.currentTarget).parent().parent().find('a').css({'background-color': 'white','font-weight': 'normal'});
                $(event.currentTarget).parent().parent().after(
                QWeb.render('SubSectionPa', {
                    count: count,
                    offset: offset,
                    account_data : account_data,
                    period_list: period_list
                }));
                $(event.currentTarget).css({
                    'background-color': '#00ede8',
                    'font-weight': 'bold',
                });
                self.loader_enable_ui()
            })
        },

        fetch_move_lines : function(event){
            event.preventDefault();
            var self = this;
            var partner_id = $(event.currentTarget).data('partner-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length == 1){
                self.loader_disable_ui();
                self.ageing_lines_by_page(offset, partner_id).then(function(datas){
                    var count = datas[0];
                    var offset = datas[1];
                    var account_data = datas[2];
                    var period_list = datas[3];
                    _.each(account_data, function (k, v){
                        var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                        };
                        if(self.filter_data['display_currency']){
                            k.range_0 = self.formatWithSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                            k.range_1 = self.formatWithSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                            k.range_2 = self.formatWithSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                            k.range_3 = self.formatWithSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                            k.range_6 = self.formatWithSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                        }else{
                            k.range_0 = self.formatWithNoSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                            k.range_1 = self.formatWithNoSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                            k.range_2 = self.formatWithNoSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                            k.range_3 = self.formatWithNoSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                            k.range_6 = self.formatWithNoSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                        }
                        k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
                    });
                    $(event.currentTarget).next('tr').removeClass('collapse');
                    $(event.currentTarget).next('tr').find('td .py-mline-table-div').remove();
                    $(event.currentTarget).next('tr').find('td ul').after(
                    QWeb.render('SubSectionPa', {
                        count: count,
                        offset: offset,
                        account_data: account_data,
                        period_list: period_list
                    }))
                    $(event.currentTarget).next('tr').find('td ul li:first a').css({
                        'background-color': '#00ede8',
                        'font-weight': 'bold',
                    });
                    self.loader_enable_ui();
                })
            }else{
                $(event.currentTarget).next('tr').find('td .py-mline-table-div').remove();
                $(event.currentTarget).next('tr').addClass('collapse');   
            }
        },

        view_move_line : function(event){
            event.preventDefault();
            var self = this;
            var context = {};
            var redirect_to_document = function (res_model, res_id, view_id) {
                var action = {
                    type:'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: res_model,
                    views: [[view_id || false, 'form']],
                    res_id: res_id,
                    target: 'current',
                    context: context,
                };
                alert(_("Redirected"), "Window has been redirected");
                return self.do_action(action);
            };
            redirect_to_document('account.move',$(event.currentTarget).data('move-id'));
        },

        update_with_filter : function(event){
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {}
            output.type = false;
            output.include_details = false;
            output.partner_type = false;
            output.bucket_1 = $("#bucket_1").val();
            output.bucket_2 = $("#bucket_2").val();
            output.bucket_3 = $("#bucket_3").val();
            if((parseInt(output.bucket_1) >= parseInt(output.bucket_2)) | (parseInt(output.bucket_2) >= parseInt(output.bucket_3))){
                alert('Bucket order must be ascending');
                return;
            }
            if($(".type-multiple").select2('data').length === 1){
                output.type = $(".type-multiple").select2('data')[0].id
            }
            if($(".partner-type-multiple").select2('data').length === 1){
                output.partner_type = $(".partner-type-multiple").select2('data')[0].id
            }
            var partner_ids = [];
            var partner_list = $(".partner-multiple").select2('data')
            for (var i=0; i < partner_list.length; i++){
                partner_ids.push(parseInt(partner_list[i].id))
            }
            output.partner_ids = partner_ids
            var partner_tag_ids = [];
            var partner_tag_list = $(".partner-tag-multiple").select2('data')
            for (var i=0; i < partner_tag_list.length; i++){
                partner_tag_ids.push(parseInt(partner_tag_list[i].id))
            }
            output.partner_category_ids = partner_tag_ids
            if ($("#as_on_date").val()){
                var dateObject = $("#as_on_date").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.as_on_date = dateString;
            }
            var options_list = $(".extra-multiple").select2('data')
            for (var i=0; i < options_list.length; i++){
                if(options_list[i].id === 'include_details'){
                    output.include_details = true;
                }
            }
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function(res){
                self.plot_data(self.initial_render);
            });
        },
        group_by_partner : function(event){
                event.preventDefault();
                var self = this;
                self.initial_render = false;
                var output = {}
                output.type = false;
                var type = self.filter_data.type
                output.include_details = false;
                output.partner_type = false;
                var partner_type = self.filter_data.partner_type

                output.bucket_1 = $("#bucket_1").val();
                output.bucket_2 = $("#bucket_2").val();
                output.bucket_3 = $("#bucket_3").val();
                if( (parseInt(output.bucket_1) >= parseInt(output.bucket_2)) |
                    (parseInt(output.bucket_2) >= parseInt(output.bucket_3))){
                    alert('Bucket order must be ascending');
                    return;
                }
                // console.log('self  : ',self)
                // console.log('type = ',$(".type-multiple").select2('data'))
                // console.log('type_2 = ',type)
                // console.log('partner = ',$(".partner-type-multiple").select2('data'))
                // console.log('partner_2 = ',partner_type)
                // console.log('detail = ',$(".extra-multiple").select2('data'))

                if($(".type-multiple").select2('data').length === 1){
                    output.type = $(".type-multiple").select2('data')[0].id
                }else{
                    output.type = type
                }

                if($(".partner-type-multiple").select2('data').length === 1){
                    output.partner_type = $(".partner-type-multiple").select2('data')[0].id
                }else{
                    output.partner_type = partner_type
                }

                var partner_ids = [];
                var partner_list = $(".partner-multiple").select2('data')
                for (var i=0; i < partner_list.length; i++){
                    partner_ids.push(parseInt(partner_list[i].id))
                }
                output.partner_ids = partner_ids
                var partner_tag_ids = [];
                var partner_tag_list = $(".partner-tag-multiple").select2('data')
                for (var i=0; i < partner_tag_list.length; i++){
                    partner_tag_ids.push(parseInt(partner_tag_list[i].id))
                }
                output.partner_category_ids = partner_tag_ids
                if ($("#as_on_date").val()){
                    var dateObject = $("#as_on_date").datepicker("getDate");
                    var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                    output.as_on_date = dateString;
                }
                var options_list = $(".extra-multiple").select2('data')
                for (var i=0; i < options_list.length; i++){
                    if(options_list[i].id === 'include_details'){
                        output.include_details = true;
                    }
                }
                self._rpc({
                    model: 'ins.partner.ageing',method: 'write',
                    args: [self.wizard_id, output],
                }).then(function(res){
                    self.plot_data_group_by_partner(self.initial_render);
                });
            },
        loader_disable_ui: function(){
            $('.py-main-container').addClass('ui-disabled');
            $('.py-main-container').css({'opacity': '0.4','cursor':'wait'});
            $('#loader').css({'visibility':'visible','opacity': '1'});
        },
        loader_enable_ui: function(){
            $('.py-main-container').removeClass('ui-disabled');
            $('#loader').css({'visibility':'hidden'});
            $('.py-main-container').css({'opacity': '1','cursor':'auto'});
        },
    });

    core.action_registry.add('dynamic_pa', DynamicPaMain);

return DynamicPaMain;

});