document.addEventListener("DOMContentLoaded", function () {

    // ============================================
    // Branch Stream Tom Select
    // ============================================

    const streamSelect = new TomSelect("#branch-stream-select", {

        plugins: ["remove_button"],

        create: false,
        persist: false,
        hideSelected: true,
        closeAfterSelect: false,

        maxOptions: null,

        placeholder: "Search or select branch streams..."

    });


    // ============================================
    // Branch Tom Select
    // ============================================

    const branchSelect = new TomSelect("#branch-select", {

        plugins: ["remove_button"],

        create: false,
        persist: false,
        hideSelected: true,
        closeAfterSelect: false,

        maxOptions: null,

        placeholder: "Select branch stream(s) first..."

    });


    // ============================================
    // Prevent Enter from auto-selecting
    // ============================================

    streamSelect.control_input.addEventListener("keydown", function (e) {

        if (e.key === "Enter" && this.value.trim() === "") {
            e.preventDefault();
        }

    });


    // ============================================
    // Clear search after every selection
    // ============================================

    streamSelect.on("item_add", function () {

        this.setTextboxValue("");
        this.refreshOptions(false);

    });


    // ============================================
    // Populate Branches dynamically
    // ============================================

    streamSelect.on("change", function () {

        branchSelect.clear(true);
        branchSelect.clearOptions();

        const selectedStreams = streamSelect.items;

        let branches = [];

        selectedStreams.forEach(stream => {

            if (BRANCH_MAPPING[stream]) {

                branches = branches.concat(BRANCH_MAPPING[stream]);

            }

        });

        let orderedBranches = [];

selectedStreams.forEach(stream => {

    if (!BRANCH_MAPPING[stream]) return;

    const sorted = [...BRANCH_MAPPING[stream]].sort((a, b) =>
        a.localeCompare(b)
    );

    orderedBranches.push(...sorted);

});

branches = orderedBranches;

        branches.forEach(branch => {

            branchSelect.addOption({

                value: branch,
                text: branch

            });

        });

        branchSelect.refreshOptions(false);

    });

});