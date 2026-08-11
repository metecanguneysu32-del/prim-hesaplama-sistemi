document.addEventListener("DOMContentLoaded", function () {

    // ============================================================
    // YIL / HAFTA
    // ============================================================

    const yearSelect = document.getElementById("year");
    const weekSelect = document.getElementById("week");

    if (weekSelect) {

        for (let week = 1; week <= 53; week++) {

            const option = document.createElement("option");

            option.value = week;
            option.textContent = `${week}. Hafta`;

            weekSelect.appendChild(option);
        }
    }


    // ============================================================
    // DOSYA SEÇİMİ
    // ============================================================

    setupFileDisplay(
        "storesFile",
        "storesSelected"
    );

    setupFileDisplay(
        "personnelFile",
        "personnelSelected"
    );

    setupFileDisplay(
        "targetsFile",
        "targetsSelected"
    );

    setupFileDisplay(
        "salesFile",
        "salesSelected"
    );


    // ============================================================
    // AKTARIM BUTONLARI
    // ============================================================

    setupImportButton(
        "storesButton",
        "storesFile",
        "storesResult",
        "storesLoading",
        "/api/import/stores",
        false
    );

    setupImportButton(
        "personnelButton",
        "personnelFile",
        "personnelResult",
        "personnelLoading",
        "/api/import/personnel",
        false
    );

    setupImportButton(
        "targetsButton",
        "targetsFile",
        "targetsResult",
        "targetsLoading",
        "/api/import/targets",
        true
    );

    setupImportButton(
        "salesButton",
        "salesFile",
        "salesResult",
        "salesLoading",
        "/api/import/sales",
        true
    );


    // ============================================================
    // DOSYA GÖSTER
    // ============================================================

    function setupFileDisplay(
        inputId,
        selectedId
    ) {

        const input = document.getElementById(inputId);
        const selected = document.getElementById(selectedId);

        if (!input || !selected) {
            return;
        }

        input.addEventListener(
            "change",
            function () {

                if (!input.files.length) {

                    selected.style.display = "none";
                    selected.textContent = "";

                    return;
                }

                const file = input.files[0];

                selected.textContent =
                    `Seçilen dosya: ${file.name}`;

                selected.style.display = "block";
            }
        );
    }


    // ============================================================
    // EXCEL AKTARIMI
    // ============================================================

    function setupImportButton(
        buttonId,
        inputId,
        resultId,
        loadingId,
        endpoint,
        needsPeriod
    ) {

        const button =
            document.getElementById(buttonId);

        const input =
            document.getElementById(inputId);

        const result =
            document.getElementById(resultId);

        const loading =
            document.getElementById(loadingId);


        if (!button || !input || !result || !loading) {
            return;
        }


        button.addEventListener(
            "click",
            async function () {

                clearResult(result);


                // ------------------------------------------------
                // DOSYA KONTROLÜ
                // ------------------------------------------------

                if (!input.files.length) {

                    showError(
                        result,
                        "Lütfen önce bir Excel dosyası seçin."
                    );

                    return;
                }


                // ------------------------------------------------
                // DÖNEM KONTROLÜ
                // ------------------------------------------------

                if (needsPeriod) {

                    if (!yearSelect || !weekSelect) {

                        showError(
                            result,
                            "Yıl ve hafta alanları bulunamadı."
                        );

                        return;
                    }


                    if (!yearSelect.value) {

                        showError(
                            result,
                            "Lütfen yıl seçin."
                        );

                        return;
                    }


                    if (!weekSelect.value) {

                        showError(
                            result,
                            "Lütfen hafta seçin."
                        );

                        return;
                    }
                }


                // ------------------------------------------------
                // FORM DATA
                // ------------------------------------------------

                const formData =
                    new FormData();

                formData.append(
                    "file",
                    input.files[0]
                );


                if (needsPeriod) {

                    formData.append(
                        "year",
                        yearSelect.value
                    );

                    formData.append(
                        "week",
                        weekSelect.value
                    );
                }


                // ------------------------------------------------
                // YÜKLENİYOR
                // ------------------------------------------------

                button.disabled = true;

                loading.style.display = "block";


                try {

                    const response =
                        await fetch(
                            endpoint,
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok || !data.success) {

                        throw new Error(
                            data.message ||
                            "Aktarım sırasında hata oluştu."
                        );
                    }


                    // ------------------------------------------------
                    // BAŞARILI
                    // ------------------------------------------------

                    let message =
                        data.message ||
                        "Aktarım tamamlandı.";


                    if (
                        data.created !== undefined
                    ) {

                        message +=
                            `<br>Yeni kayıt: ${data.created}`;
                    }


                    if (
                        data.updated !== undefined
                    ) {

                        message +=
                            `<br>Güncellenen kayıt: ${data.updated}`;
                    }


                    if (
                        data.count !== undefined
                    ) {

                        message +=
                            `<br>Aktarılan kayıt: ${data.count}`;
                    }


                    if (
                        data.skipped !== undefined
                    ) {

                        message +=
                            `<br>Atlanan kayıt: ${data.skipped}`;
                    }


                    showSuccess(
                        result,
                        message
                    );


                } catch (error) {

                    showError(
                        result,
                        error.message
                    );


                } finally {

                    button.disabled = false;

                    loading.style.display = "none";
                }

            }
        );
    }


    // ============================================================
    // SONUÇ TEMİZLE
    // ============================================================

    function clearResult(result) {

        result.style.display = "none";

        result.className =
            "result-box";

        result.innerHTML = "";
    }


    // ============================================================
    // BAŞARILI MESAJ
    // ============================================================

    function showSuccess(
        result,
        message
    ) {

        result.className =
            "result-box result-success";

        result.innerHTML =
            `✓ ${message}`;

        result.style.display = "block";
    }


    // ============================================================
    // HATA MESAJI
    // ============================================================

    function showError(
        result,
        message
    ) {

        result.className =
            "result-box result-error";

        result.innerHTML =
            `✗ ${message}`;

        result.style.display = "block";
    }

});
