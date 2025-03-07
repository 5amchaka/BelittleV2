/**
 * Gestion de l'affichage des colonnes du tableau
 */

// Fonction pour sauvegarder l'état des colonnes dans localStorage
function saveColumnState() {
  const columnStates = {};
  
  for (let i = 0; i < 8; i++) {
    const checkbox = document.getElementById(`column-${i}`);
    if (checkbox) {
      columnStates[i] = checkbox.checked;
    }
  }
  
  localStorage.setItem('columnStates', JSON.stringify(columnStates));
}

// Fonction pour charger l'état des colonnes depuis localStorage
function loadColumnState() {
  const storedStates = localStorage.getItem('columnStates');
  if (storedStates) {
    const columnStates = JSON.parse(storedStates);
    
    for (let i = 0; i < 8; i++) {
      const checkbox = document.getElementById(`column-${i}`);
      if (checkbox && columnStates[i] !== undefined) {
        checkbox.checked = columnStates[i];
        toggleColumn(i, false);
      }
    }
  }
}

// Fonction pour afficher/masquer les colonnes
function toggleColumn(columnIndex, save = true) {
  let table = document.getElementById('resultsTable');
  let rows = table.getElementsByTagName('tr');
  let checkbox = document.getElementById(`column-${columnIndex}`);
  let isChecked = checkbox.checked;
  
  for (let i = 0; i < rows.length; i++) {
    let cells = rows[i].getElementsByTagName(i === 0 ? 'th' : 'td');
    if (cells.length > columnIndex) {
      cells[columnIndex].style.display = isChecked ? '' : 'none';
    }
  }
  
  // Sauvegarder l'état si demandé
  if (save) {
    saveColumnState();
  }
}

/**
 * Tri du tableau de résultats
 */
function sortTable(columnIndex) {
  let table = document.getElementById('resultsTable');
  let tbody = table.querySelector('tbody');
  let rows = Array.from(tbody.querySelectorAll('tr'));
  let th = table.querySelector('th:nth-child(' + (columnIndex + 1) + ')');
  let isAscending = !th.classList.contains('sorted-asc');
  
  // Supprimer les classes de tri de tous les en-têtes
  table.querySelectorAll('th').forEach(header => {
    header.classList.remove('sorted-asc', 'sorted-desc');
  });
  
  // Ajouter la classe appropriée à l'en-tête actuel
  th.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
  
  // Trier les lignes
  rows.sort((rowA, rowB) => {
    let cellA = rowA.querySelector('td:nth-child(' + (columnIndex + 1) + ')').textContent.trim().toLowerCase();
    let cellB = rowB.querySelector('td:nth-child(' + (columnIndex + 1) + ')').textContent.trim().toLowerCase();
    
    if (cellA < cellB) {
      return isAscending ? -1 : 1;
    }
    if (cellA > cellB) {
      return isAscending ? 1 : -1;
    }
    return 0;
  });
  
  // Réorganiser les lignes dans le tableau
  rows.forEach(row => tbody.appendChild(row));
}

/**
 * Filtrage du tableau de résultats
 */
function filterTable() {
  let input = document.getElementById('search-input');
  let filter = input.value.toLowerCase();
  let table = document.getElementById('resultsTable');
  let rows = table.getElementsByTagName('tr');
  
  for (let i = 1; i < rows.length; i++) {
    let found = false;
    let cells = rows[i].getElementsByTagName('td');
    
    for (let j = 0; j < cells.length - 1; j++) { // Exclure la colonne "Actions"
      let cell = cells[j];
      if (cell) {
        let text = cell.textContent || cell.innerText;
        if (text.toLowerCase().indexOf(filter) > -1) {
          found = true;
          break;
        }
      }
    }
    
    rows[i].style.display = found ? '' : 'none';
  }
}

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
  // Ajouter des écouteurs d'événements aux cases à cocher
  for (let i = 0; i < 8; i++) {
    const checkbox = document.getElementById(`column-${i}`);
    if (checkbox) {
      checkbox.addEventListener('change', function() {
        toggleColumn(i);
      });
    }
  }
  
  // Charger l'état des colonnes
  loadColumnState();
});