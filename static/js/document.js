/**
 * Filtrage des entreprises dans les sélecteurs
 */
function filterEnterprises() {
  const search = document.getElementById('enterprise-search').value.toLowerCase();
  const items = document.querySelectorAll('.enterprise-item');
  
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    if (text.includes(search)) {
      item.style.display = '';
    } else {
      item.style.display = 'none';
    }
  });
}

/**
 * Gestion du formulaire DC1: glisser-déposer des cotraitants
 */
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si on est sur la page du formulaire DC1
  const cotraitantsContainer = document.getElementById('cotraitants-container');
  
  if (cotraitantsContainer) {
    const draggableItems = document.querySelectorAll('.draggable-item');
    const hiddenCotraitants = document.getElementById('hidden-cotraitants');
    let cotraitants = [];
    
    // Configuration des éléments glissables
    draggableItems.forEach(item => {
      item.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', this.dataset.id);
      });
    });
    
    // Événements pour la zone de dépôt
    cotraitantsContainer.addEventListener('dragover', function(e) {
      e.preventDefault();
      cotraitantsContainer.classList.add('dragover');
    });
    
    cotraitantsContainer.addEventListener('dragleave', function(e) {
      e.preventDefault();
      cotraitantsContainer.classList.remove('dragover');
    });
    
    cotraitantsContainer.addEventListener('drop', function(e) {
      e.preventDefault();
      cotraitantsContainer.classList.remove('dragover');
      
      const id = e.dataTransfer.getData('text/plain');
      const item = document.querySelector(`.draggable-item[data-id="${id}"]`);
      
      if (item && !cotraitants.includes(id)) {
        // Ajouter à la liste des cotraitants
        cotraitants.push(id);
        
        // Créer un élément pour représenter le cotraitant
        const cotraitantItem = document.createElement('div');
        cotraitantItem.className = 'cotraitant-item';
        cotraitantItem.dataset.id = id;
        
        const cotraitantInfo = document.createElement('div');
        cotraitantInfo.className = 'cotraitant-info';
        cotraitantInfo.innerHTML = `
          <strong>${item.dataset.name}</strong>
          ${item.dataset.siret ? `<small>SIRET: ${item.dataset.siret}</small>` : ''}
        `;
        
        // Ajouter un champ pour la prestation
        const prestationInput = document.createElement('div');
        prestationInput.className = 'prestation-input';
        prestationInput.innerHTML = `
          <label>Prestation:</label>
          <input type="text" class="cotraitant-prestation" data-id="${id}" placeholder="Prestation du cotraitant">
        `;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'remove-cotraitant';
        removeButton.textContent = '×';
        removeButton.addEventListener('click', function() {
          removeCotraitant(id);
        });
        
        cotraitantItem.appendChild(cotraitantInfo);
        cotraitantItem.appendChild(prestationInput);
        cotraitantItem.appendChild(removeButton);
        
        // Supprimer le message vide si c'est le premier cotraitant
        const emptyMessage = cotraitantsContainer.querySelector('.empty-message');
        if (emptyMessage) {
          emptyMessage.remove();
        }
        
        cotraitantsContainer.appendChild(cotraitantItem);
        updateHiddenFields();
      }
    });
    
    // Fonction pour supprimer un cotraitant
    window.removeCotraitant = function(id) {
      const index = cotraitants.indexOf(id);
      if (index > -1) {
        cotraitants.splice(index, 1);
      }
      
      const item = cotraitantsContainer.querySelector(`.cotraitant-item[data-id="${id}"]`);
      if (item) {
        item.remove();
      }
      
      // Si aucun cotraitant, afficher le message vide
      if (cotraitants.length === 0) {
        const emptyMessage = document.createElement('p');
        emptyMessage.className = 'empty-message';
        emptyMessage.textContent = 'Glissez les entreprises ici pour les ajouter comme co-traitants.';
        cotraitantsContainer.appendChild(emptyMessage);
      }
      
      updateHiddenFields();
    };
    
    // Mettre à jour les champs cachés pour le formulaire
    function updateHiddenFields() {
      // Vider les champs cachés existants
      hiddenCotraitants.innerHTML = '';
      
      // Créer un champ caché pour chaque cotraitant
      cotraitants.forEach(id => {
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';
        hiddenField.name = 'cotraitant_ids';
        hiddenField.value = id;
        hiddenCotraitants.appendChild(hiddenField);
        
        // Récupérer la prestation si elle a été saisie
        const prestationInput = document.querySelector(`.cotraitant-prestation[data-id="${id}"]`);
        if (prestationInput) {
          const prestationField = document.createElement('input');
          prestationField.type = 'hidden';
          prestationField.name = `cotraitant_prestation_${id}`;
          prestationField.value = prestationInput.value;
          hiddenCotraitants.appendChild(prestationField);
        }
      });
    }
  }
});