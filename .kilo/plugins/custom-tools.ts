import type { Plugin } from "@opencode-ai/plugin";
import jsonRepair from "../tools/json_repair";
import hashlineEdit from "../tools/hashline_edit";
import { read as hashline_read, grep as hashline_grep } from "../tools/hashline_rg";
import { search as astGrepSearch } from "../tools/ast_grep";

const CustomToolsPlugin: Plugin = async () => ({
  tool: {
    json_repair: jsonRepair,
    hashline_edit: hashlineEdit,
    hashline_read,
    hashline_grep,
    ast_grep: astGrepSearch,
  },
});

export default CustomToolsPlugin;
