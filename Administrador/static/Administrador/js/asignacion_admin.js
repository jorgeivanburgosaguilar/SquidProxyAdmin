window.onload = function () {
  if (typeof django !== "undefined" && typeof django.jQuery !== "undefined") {
    (function ($) {
      "use strict";
      function reloadIPDropdown() {
        const redSelect = $("#id_red");
        const ipSelect = $("#id_ip");
        if (redSelect.length === 0) return;
        const currentValue = ipSelect.val();

        redSelect.on("change", function () {
          const selectedRed = $(this).val();

          $.ajax({
            url: "/admin/update-ip-choices/",
            data: {
              red_id: selectedRed,
              current_value: currentValue,
            },
          })
            .done(function (data) {
              ipSelect.empty();
              const options = data.choices.map(function (choice) {
                return $("<option></option>")
                  .attr("value", choice[0])
                  .text(choice[1]);
              });
              ipSelect.append(options);
              if (currentValue) {
                ipSelect.val(currentValue);
              }
            })
            .fail(function () {
              ipSelect.empty();
              ipSelect.append($("<option value=''>---------</option>"));
            });
        });
      }

      reloadIPDropdown();
    })(django.jQuery);
  }
};
