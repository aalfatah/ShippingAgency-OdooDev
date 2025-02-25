/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class CostStructureListController extends ListController {
   setup() {
       super.setup();
   }
   syncCostStructure() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'sync.rate.card.wizard',
          name:'Sync. Rate Card',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
//          context: {'default_order_id': order_id},
          target: 'new',
          res_id: false,
      });
   }
}
/*

const viewRegistry = registry.category("views");
export const CSListController = {
    ...listView,
    Controller: CostStructureListController,
}
viewRegistry.add("cost_structure_list_controller", CSListController);
*/
registry.category("views").add("cost_structure_list_controller", {
   ...listView,
   Controller: CostStructureListController,
   buttonTemplate: "sale_port_agency_dev.ListView.Buttons",
});
