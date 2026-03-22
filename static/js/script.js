/* ============================================
   EXPIRY TRACKER — FINAL JS (CLEAN VERSION)
   ============================================ */

$(document).ready(function () {

  /* ---------- SWEET ALERT HELPER ---------- */
  function showAlert(icon, message) {
    Swal.fire({
      icon: icon,
      title: message,
      timer: 2000,
      showConfirmButton: false
    });
  }

  /* ---------- PASSWORD STRENGTH ---------- */
  $("#password").on("input", function () {
    const val = $(this).val();
    const bar = $("#pw-bar");
    const hint = $("#pw-hint");

    if (!bar.length) return;

    let strength = 0;

    if (val.length >= 6) strength++;
    if (/[A-Z]/.test(val)) strength++;
    if (/[0-9]/.test(val)) strength++;
    if (/[^A-Za-z0-9]/.test(val)) strength++;

    let width = (strength / 4) * 100;
    bar.css("width", width + "%");

    if (strength <= 1) {
      bar.removeClass().addClass("progress-bar bg-danger");
      hint.text("Weak password");
    } else if (strength === 2) {
      bar.removeClass().addClass("progress-bar bg-warning");
      hint.text("Medium strength");
    } else {
      bar.removeClass().addClass("progress-bar bg-success");
      hint.text("Strong password");
    }
  });

  /* ---------- REGISTER VALIDATION ---------- */
  $("#register-form").submit(function (e) {
    const username = $("#username").val().trim();
    const password = $("#password").val();
    const email = $("#email").val().trim();

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!username || !password || !email) {
      e.preventDefault();
      showAlert("error", "All fields are required");
      return;
    }

    if (username.length < 3) {
      e.preventDefault();
      showAlert("error", "Username must be at least 3 characters");
      return;
    }

    if (password.length < 6) {
      e.preventDefault();
      showAlert("error", "Password must be at least 6 characters");
      return;
    }

    if (!emailPattern.test(email)) {
      e.preventDefault();
      showAlert("error", "Enter a valid email address");
      return;
    }
  });

  /* ---------- LOGIN VALIDATION ---------- */
  $("#login-form").submit(function (e) {
    const username = $("#username").val().trim();
    const password = $("#password").val().trim();

    if (!username || !password) {
      e.preventDefault();
      showAlert("error", "Please fill in all fields");
      return;
    }
  });

  /* ---------- ADD ITEM VALIDATION ---------- */
  $("#item-form").submit(function (e) {
    const name = $("#name").val().trim();
    const expiry = $("#expiry_date").val();
    const reminder = $("#reminder_days").val();

    if (!name) {
      e.preventDefault();
      showAlert("error", "Item name is required");
      return;
    }

    if (!expiry) {
      e.preventDefault();
      showAlert("error", "Expiry date is required");
      return;
    }

    const today = new Date().toISOString().split("T")[0];

    if (expiry < today) {
      showAlert("warning", "This item is already expired!");
      // allow submission (important UX improvement)
    }

    if (reminder && (parseInt(reminder) < 0)) {
      e.preventDefault();
      showAlert("error", "Reminder days must be 0 or more");
      return;
    }
  });

  /* ---------- DELETE CONFIRMATION ---------- */
  $(document).on("click", ".btn-delete", function (e) {
    e.preventDefault();

    const href = $(this).attr("href");
    const name = $(this).data("name") || "this item";

    Swal.fire({
      title: "Remove item?",
      html: `Are you sure you want to remove <strong>${name}</strong>?`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, remove",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#dc3545"
    }).then((result) => {
      if (result.isConfirmed) {
        window.location.href = href;
      }
    });
  });

  /* ---------- SET MIN DATE ---------- */
  const expiryInput = $("#expiry_date");
  if (expiryInput.length) {
    const today = new Date().toISOString().split("T")[0];
    expiryInput.attr("min", today);
  }

  /* ---------- FILTER TABLE ---------- */
  const textInput = $("#filter-input");
  const statusSelect = $("#status-filter");
  const rows = $("#items-table tbody tr");
  const noResults = $("#no-results");

  function applyFilters() {
    const query = textInput.val()?.toLowerCase() || "";
    const status = statusSelect.val();
    let visible = 0;

    rows.each(function () {
      const row = $(this);
      const text = row.text().toLowerCase();
      const rowStatus = row.data("status");

      const matchText = text.includes(query);
      const matchStatus = !status || rowStatus === status;

      if (matchText && matchStatus) {
        row.show();
        visible++;
      } else {
        row.hide();
      }
    });

    if (noResults.length) {
      noResults.toggleClass("d-none", visible !== 0);
    }
  }

  textInput.on("input", applyFilters);
  statusSelect.on("change", applyFilters);

});