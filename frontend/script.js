// script.js

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOMContentLoaded: Starting...");
  setupEventListeners();
  loadIngredients();
  initializeTooltips();
});

function setupEventListeners() {
  console.log("Setting up event listeners.");
  const recipeForm = document.getElementById("recipe-form");
  recipeForm.addEventListener("submit", handleFormSubmit);

  const numResultsSlider = document.getElementById("num-results");
  const numResultsValue = document.getElementById("num-results-value");
  numResultsSlider.addEventListener("input", () => {
    numResultsValue.textContent = `${numResultsSlider.value} recipes`;
    console.log("Results number slider updated:", numResultsSlider.value);
  });
}

function initializeTooltips() {
  console.log("Initializing tooltips.");
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((tooltip) => {
    new bootstrap.Tooltip(tooltip);
  });
}

async function loadIngredients() {
  console.log("Loading ingredients from API...");
  try {
    const response = await fetch(`${API_URL}/unique_ingredients`);
    if (!response.ok) {
      throw new Error("Ingredients could not be retrieved");
    }
    const ingredients = await response.json();
    console.log("Ingredients retrieved:", ingredients);
    const select = document.getElementById("ingredients");
    select.innerHTML = "";
    ingredients.sort().forEach((ingredient) => {
      const option = document.createElement("option");
      option.value = ingredient;
      option.textContent = ingredient
        .toLowerCase()
        .split(",")
        .map((word) => word.trim())
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(", ");
      select.appendChild(option);
    });
    enableIngredientSearch();
  } catch (error) {
    console.error("Error while loading ingredients:", error);
    showToast(
      "Ingredients could not be loaded. Please try again later.",
      "error"
    );
  }
}

function enableIngredientSearch() {
  console.log("Enabling ingredient search.");
  const ingredientSelect = document.getElementById("ingredients");
  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.className = "form-control mb-2";
  searchInput.placeholder = "Search ingredients...";
  ingredientSelect.parentNode.insertBefore(searchInput, ingredientSelect);
  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const options = ingredientSelect.options;
    for (let option of options) {
      const text = option.text.toLowerCase();
      option.style.display = text.includes(searchTerm) ? "" : "none";
    }
    console.log("Search term:", searchTerm);
  });
}

function getSelectedValues(selectId) {
  const select = document.getElementById(selectId);
  return select
    ? Array.from(select.selectedOptions).map((opt) => opt.value.trim())
    : [];
}

/**
 * Joins multiple selected options with a comma, matching how
 * your CSV might store "oven, pot" or "North America, Oceania".
 */
function getCommaJoinedValues(selectId) {
  const selected = getSelectedValues(selectId);
  if (selected.length === 0) {
    return ""; // no selection
  }
  // e.g. ["oven", "pot"] => "oven, pot"
  return selected.join(", ");
}

function getFormData() {
  return {
    // Instead of picking just the first selected cooking method,
    // we join them with commas so it can match "oven, pot" in the CSV if needed.
    cooking_method: getCommaJoinedValues("cooking-method"),

    servings_bin: document.getElementById("servings").value,

    // Diet types can stay as an array (the back-end code is already splitting them).
    diet_types: getSelectedValues("diet-types"),

    // Same for meal types
    meal_type: getSelectedValues("meal-types"),

    cook_time: document.getElementById("cook-time").value,

    // Health types are still arrays
    health_types: [
      ...getSelectedValues("protein-level"),
      ...getSelectedValues("carb-level"),
      ...getSelectedValues("fat-level"),
      ...getSelectedValues("calorie-level"),
      ...getSelectedValues("cholesterol-level"),
      ...getSelectedValues("sugar-level"),
    ],

    // Join multiple cuisine regions with commas, matching CSV nodes like "North America, Latin America"
    cuisine_region: getCommaJoinedValues("cuisine-region"),

    ingredients: getSelectedValues("ingredients"),

    top_k: parseInt(document.getElementById("num-results").value),
    flexible: document.getElementById("flexible-matching").checked,
  };
}

function validateFormData(formData) {
  const valid =
    formData.cooking_method ||
    formData.servings_bin ||
    formData.diet_types.length > 0 ||
    formData.meal_type.length > 0 ||
    formData.cook_time ||
    formData.health_types.length > 0 ||
    formData.cuisine_region ||
    formData.ingredients.length > 0;
  console.log("Are the form data valid?:", valid);
  return valid;
}

async function handleFormSubmit(event) {
  event.preventDefault();
  console.log("Form submitted. Collecting form data...");
  const submitButton = event.target.querySelector('button[type="submit"]');
  const originalButtonText = submitButton.textContent;
  submitButton.innerHTML = '<span class="loading"></span> Generating Recipe...';
  submitButton.disabled = true;

  try {
    const formData = getFormData();
    console.log("Form data:", formData);
    if (!validateFormData(formData)) {
      throw new Error("Please fill in at least one search criterion");
    }
    // Use the visual recipe endpoint
    const response = await fetch(`${API_URL}/generate_recipe_visual`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to generate recipe");
    }
    const recipe = await response.json();
    console.log("Generated visual recipe:", recipe);
    displayGeneratedRecipe(recipe);
  } catch (error) {
    console.error("Error while generating recipe:", error);
    showToast(error.message, "error");
  } finally {
    submitButton.textContent = originalButtonText;
    submitButton.disabled = false;
  }
}

function displayGeneratedRecipe(recipe) {
  const generatedSection = document.getElementById("generated-recipe-section");
  const generatedDiv = document.getElementById("generated-recipe");
  generatedDiv.innerHTML = formatGeneratedRecipe(recipe);
  generatedSection.style.display = "block";
}

function formatGeneratedRecipe(recipe) {
  const recipeData = recipe.recipe || {};
  const cookTime = recipeData.cook_time || recipeData.cookingTime || "N/A";
  const servings = recipeData.servings || "N/A";

  const ingredients = Array.isArray(recipeData.ingredients)
    ? recipeData.ingredients
    : [];

  let instructions = [];
  if (Array.isArray(recipeData.instructions)) {
    instructions = recipeData.instructions;
  } else if (Array.isArray(recipeData.steps)) {
    instructions = recipeData.steps;
  }

  const formattedIngredients = ingredients
    .map((ing) =>
      typeof ing === "object" && ing !== null && ing.name
        ? `<li>${ing.name}</li>`
        : `<li>${ing}</li>`
    )
    .join("");

  const formattedInstructions = instructions
    .map((step) => {
      if (typeof step === "object" && step !== null) {
        return `<li>${step.description || step.text || ""}</li>`;
      }
      return `<li>${step}</li>`;
    })
    .join("");

  return `
    <h3>${recipe.title || "No Title"}</h3>
    <p><strong>Description:</strong> ${
      recipe.description || "No description provided."
    }</p>
    <p><strong>Cook Time:</strong> ${cookTime}</p>
    <p><strong>Servings:</strong> ${servings}</p>
    <h4>Ingredients:</h4>
    <ul>${formattedIngredients}</ul>
    <h4>Instructions:</h4>
    <ol>${formattedInstructions}</ol>
    ${
      recipeData.notes
        ? `<p><strong>Notes:</strong> ${recipeData.notes}</p>`
        : ""
    }
    <div class="mt-4">
      <h4>Dish Representation:</h4>
      <img src="${
        recipe.image_url || ""
      }" alt="Generated Dish Image" class="img-fluid rounded" />
    </div>
  `;
}

function showToast(message, type = "info") {
  console.log(`Showing toast notification: ${message}`);
  const toastContainer =
    document.querySelector(".toast-container") || createToastContainer();
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-white bg-${
    type === "error" ? "danger" : "primary"
  } border-0`;
  toast.setAttribute("role", "alert");
  toast.setAttribute("aria-live", "assertive");
  toast.setAttribute("aria-atomic", "true");
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;
  toastContainer.appendChild(toast);
  const bsToast = new bootstrap.Toast(toast);
  bsToast.show();
  toast.addEventListener("hidden.bs.toast", () => {
    toast.remove();
  });
}

function createToastContainer() {
  const container = document.createElement("div");
  container.className = "toast-container position-fixed top-0 end-0 p-3";
  document.body.appendChild(container);
  return container;
}
