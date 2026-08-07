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
// College Tom Select
// ============================================

const collegeSelect = new TomSelect("#college-select", {

    plugins: ["remove_button"],

    create: false,
    persist: false,
    hideSelected: true,
    closeAfterSelect: false,

    maxOptions: null,

    placeholder: "Search or select colleges..."

});

/// ============================================
// Load Colleges
// ============================================

function loadColleges(branches = []) {

    collegeSelect.clear(true);
    collegeSelect.clearOptions();

    let url = "/api/colleges";

    if (branches.length > 0) {

        const params = new URLSearchParams();

        branches.forEach(branch => {
            params.append("branch", branch);
        });

        url = "/api/colleges-by-branches?" + params.toString();

    }

    fetch(url)
        .then(response => response.json())
        .then(data => {

            data.colleges.forEach(college => {

                collegeSelect.addOption({

                    value: college,
                    text: college

                });

            });

            collegeSelect.refreshOptions(false);

            // Restore previously selected colleges
if (typeof SELECTED_COLLEGES !== "undefined") {

    SELECTED_COLLEGES.forEach(college => {

        if (collegeSelect.options[college]) {
            collegeSelect.addItem(college, true);
        }

    });

}

        })
        .catch(error => {

            console.error("Error loading colleges:", error);

        });

}


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
// Restore previously selected branches
if (
    typeof SELECTED_BRANCHES !== "undefined" &&
    SELECTED_BRANCHES.length > 0
) {

    branchSelect.setValue(SELECTED_BRANCHES);

}

loadColleges(branchSelect.items);

    });

    // ============================================
// Reload colleges when branches change
// ============================================

branchSelect.on("change", function () {

    const selectedBranches = branchSelect.items;

    loadColleges(selectedBranches);

});

// ============================================
// Restore previous selections
// ============================================

if (
    typeof SELECTED_STREAMS !== "undefined" &&
    SELECTED_STREAMS.length > 0
) {

    streamSelect.setValue(SELECTED_STREAMS);

} else {

    loadColleges();

}

// ============================================
// Search Form Validation
// ============================================

const searchForm = document.querySelector("form");

searchForm.addEventListener("submit", function (e) {

    // Clear previous Branch Stream error
    document.getElementById("stream-error").textContent = "";

    const year = document.querySelector('select[name="year"]').value;
    const category = document.querySelector('select[name="category"]').value;
    const minRank = document.getElementById("min-rank").value.trim();
    const maxRank = document.getElementById("max-rank").value.trim();

    let valid = true;

    // Branch Stream validation
    if (streamSelect.items.length === 0) {

        document.getElementById("stream-error").textContent =
            "Please select at least one Branch Stream.";

        valid = false;
    }

    // Rank validation
    if (
        minRank !== "" &&
        maxRank !== "" &&
        parseInt(minRank) > parseInt(maxRank)
    ) {

        alert("From Rank cannot be greater than To Rank.");
        valid = false;
    }

    if (!valid) {
        e.preventDefault();
    }

});
});