window.onload = function () {
  if (typeof django !== "undefined" && typeof django.jQuery !== "undefined") {
    (function ($) {
      "use strict";
      const redSelect = $("#id_red");
      if (redSelect.length === 0) return;

      const ipSelect = $("#id_ip");
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

      const macInput = $("#id_mac");
      macInput.on("paste", function (event) {
        event.preventDefault();
        const pastedText = event.originalEvent.clipboardData.getData("text");
        const cleanedInput = pastedText
          .replace(/[^a-zA-Z0-9]/g, "")
          .toUpperCase();
        const groups = cleanedInput.match(/.{1,2}/g);
        if (groups && groups.length > 0) macInput.val(groups.join(":"));
      });
    })(django.jQuery);
  }
};
