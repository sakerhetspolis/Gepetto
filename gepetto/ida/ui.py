import random
import string

import idaapi
import ida_hexrays

import gepetto.config
from gepetto.ida.handlers import ExplainHandler, RenameHandler, SwapModelHandler

_ = gepetto.config.translate.gettext

class GepettoPlugin(idaapi.plugin_t):
    flags = 0
    explain_action_name = "gepetto:explain_function"
    explain_menu_path = "Edit/Gepetto/" + _("Explain function")
    rename_action_name = "gepetto:rename_function"
    rename_menu_path = "Edit/Gepetto/" + _("Rename variables")

    # Model selection menu
    select_gpt35_action_name = "gepetto:select_gpt35"
    select_gpt4_action_name = "gepetto:select_gpt4"
    select_gpt35_menu_path = "Edit/Gepetto/" + _("gpt-3.5-turbo")
    select_gpt4_menu_path = "Edit/Gepetto/" + _("gpt-4")

    # Combined actions
    combined_gpt35_action_name = "gepetto:combined_gpt35"
    combined_gpt4_action_name = "gepetto:combined_gpt4"
    combined_gpt35_menu_path = "Edit/Gepetto/" + _("Explain & Rename with gpt-3.5-turbo")
    combined_gpt4_menu_path = "Edit/Gepetto/" + _("Explain & Rename with gpt-4")

    wanted_name = 'Gepetto'
    wanted_hotkey = ''
    comment = _("Uses {model} to enrich the decompiler's output").format(model=str(gepetto.config.model))
    help = _("See usage instructions on GitHub")
    menu = None

    def init(self):
        if not ida_hexrays.init_hexrays_plugin():
            return idaapi.PLUGIN_SKIP

        explain_action = idaapi.action_desc_t(self.explain_action_name,
                                              _('Explain function'),
                                              ExplainHandler(),
                                              "Ctrl+Alt+G",
                                              _('Use {model} to explain the currently selected function').format(
                                                  model=str(gepetto.config.model)),
                                              201)
        idaapi.register_action(explain_action)
        idaapi.attach_action_to_menu(self.explain_menu_path, self.explain_action_name, idaapi.SETMENU_APP)

        rename_action = idaapi.action_desc_t(self.rename_action_name,
                                             _('Rename variables'),
                                             RenameHandler(),
                                             "Ctrl+Alt+R",
                                             _("Use {model} to rename this function's variables").format(
                                                 model=str(gepetto.config.model)),
                                             201)
        idaapi.register_action(rename_action)
        idaapi.attach_action_to_menu(self.rename_menu_path, self.rename_action_name, idaapi.SETMENU_APP)

        self.generate_plugin_select_menu()

        self.menu = ContextMenuHooks()
        self.menu.hook()

        return idaapi.PLUGIN_KEEP

    def generate_plugin_select_menu(self):
        idaapi.unregister_action(self.select_gpt35_action_name)
        idaapi.unregister_action(self.select_gpt4_action_name)
        idaapi.detach_action_from_menu(self.select_gpt35_menu_path, self.select_gpt35_action_name)
        idaapi.detach_action_from_menu(self.select_gpt4_menu_path, self.select_gpt4_action_name)

        self.select_gpt35_action_name = f"gepetto:{''.join(random.choices(string.ascii_lowercase, k=7))}"
        self.select_gpt4_action_name = f"gepetto:{''.join(random.choices(string.ascii_lowercase, k=7))}"


        select_gpt35_action = idaapi.action_desc_t(self.select_gpt35_action_name,
                                                   "gpt-3.5-turbo",
                                                   None if str(gepetto.config.model) == "gpt-3.5-turbo"
                                                   else SwapModelHandler("gpt-3.5-turbo", self),
                                                   "1",
                                                   "",
                                                   208 if str(gepetto.config.model) == "gpt-3.5-turbo" else 0)

        idaapi.register_action(select_gpt35_action)
        idaapi.attach_action_to_menu(self.select_gpt35_menu_path, self.select_gpt35_action_name, idaapi.SETMENU_APP)

        select_gpt4_action = idaapi.action_desc_t(self.select_gpt4_action_name,
                                                  "gpt-4",
                                                  None if str(gepetto.config.model) == "gpt-4"
                                                  else SwapModelHandler("gpt-4", self),
                                                  "1",
                                                  "",
                                                  208 if str(gepetto.config.model) == "gpt-4" else 0)
        idaapi.register_action(select_gpt4_action)
        idaapi.attach_action_to_menu(self.select_gpt4_menu_path, self.select_gpt4_action_name, idaapi.SETMENU_APP)

        # Combined gpt-3.5-turbo action
        combined_gpt35_action = idaapi.action_desc_t(self.combined_gpt35_action_name,
                                                     "Explain & Rename with gpt-3.5-turbo",
                                                     CombinedHandler("gpt-3.5-turbo", self),
                                                     "3",
                                                     "",
                                                     0)

        idaapi.register_action(combined_gpt35_action)
        idaapi.attach_action_to_menu(self.combined_gpt35_menu_path, self.combined_gpt35_action_name, idaapi.SETMENU_APP)

        # Combined gpt-4 action
        combined_gpt4_action = idaapi.action_desc_t(self.combined_gpt4_action_name,
                                                    "Explain & Rename with gpt-4",
                                                    CombinedHandler("gpt-4", self),
                                                    "4",
                                                    "",
                                                    0)
        idaapi.register_action(combined_gpt4_action)
        idaapi.attach_action_to_menu(self.combined_gpt4_menu_path, self.combined_gpt4_action_name, idaapi.SETMENU_APP)

    def run(self, arg):
        pass

    def term(self):
        idaapi.detach_action_from_menu(self.explain_menu_path, self.explain_action_name)
        idaapi.detach_action_from_menu(self.rename_menu_path, self.rename_action_name)
        idaapi.detach_action_from_menu(self.select_gpt35_menu_path, self.select_gpt35_action_name)
        idaapi.detach_action_from_menu(self.select_gpt4_menu_path, self.select_gpt4_action_name)
        idaapi.detach_action_from_menu(self.combined_gpt35_menu_path, self.combined_gpt35_action_name)
        idaapi.detach_action_from_menu(self.combined_gpt4_menu_path, self.combined_gpt4_action_name)
        if self.menu:
            self.menu.unhook()
        return

class ContextMenuHooks(idaapi.UI_Hooks):
    def finish_populating_widget_popup(self, form, popup):
        if idaapi.get_widget_type(form) == idaapi.BWN_PSEUDOCODE:
            idaapi.attach_action_to_popup(form, popup, GepettoPlugin.explain_action_name, "Gepetto/")
            idaapi.attach_action_to_popup(form, popup, GepettoPlugin.rename_action_name, "Gepetto/")

from gepetto.models.base import get_model

class CombinedHandler(idaapi.action_handler_t):
    def __init__(self, model, plugin):
        self.model = model
        self.plugin = plugin

    def activate(self, ctx):
        # Swap the model
        gepetto.config.model = get_model(self.model)

        # Update the menu
        self.plugin.generate_plugin_select_menu()

        # Execute the "Explain function" action
        idaapi.process_ui_action(self.plugin.explain_action_name)

        # Execute the "Rename variables" action
        idaapi.process_ui_action(self.plugin.rename_action_name)

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS
