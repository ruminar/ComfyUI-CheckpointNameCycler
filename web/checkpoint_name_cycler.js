import { app } from "../../scripts/app.js";

const EXTENSION_NAME = "ruminar.CheckpointNameCycler";
const NODE_NAME = "CheckpointNameCycler";

function shorten(text, maxLength = 64) {
    const value = String(text ?? "");
    if (value.length <= maxLength) {
        return value;
    }
    return value.slice(0, maxLength - 3) + "...";
}

app.registerExtension({
    name: EXTENSION_NAME,

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (String(nodeData?.name ?? "") !== NODE_NAME) {
            return;
        }

        const originalOnExecuted = nodeType.prototype.onExecuted;

        nodeType.prototype.onExecuted = function (message) {
            originalOnExecuted?.apply(this, arguments);

            const ckptName = message?.ckpt_name?.[0] ?? "";
            const repeatIndex = Number(message?.repeat_index?.[0] ?? 0);
            const changeEvery = Number(message?.change_every?.[0] ?? 1);

            if (!ckptName) {
                this.title = "Checkpoint Name Cycler";
            } else if (changeEvery <= 1) {
                this.title = `Cp: ${shorten(ckptName)}`;
            } else {
                this.title = `Cp: ${shorten(ckptName)} (${repeatIndex}/${changeEvery})`;
            }

            this.setDirtyCanvas?.(true, true);
            app.graph?.setDirtyCanvas?.(true, true);
        };
    },
});
