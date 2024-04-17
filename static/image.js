document.addEventListener('DOMContentLoaded', () => {
    const filtersContainer = document.querySelector('.filters-container');
    const sliderContainer = document.querySelector('.slider-container');
    const effectsContainer = document.querySelector('.effects-container');
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    let image = new Image();
    let appliedFilters = [];
    const reset = document.getElementById("reset-file");
    const save = document.getElementById("save-file");

    // Add event listener to each filter button
    filtersContainer.querySelectorAll('.filter-btn').forEach(button => {
        button.addEventListener('click', () => {
            const filterName = button.textContent.toLowerCase();
            createSlider(filterName);
        });
    });

    effectsContainer.querySelectorAll('.effect-btn').forEach(button => {
        button.addEventListener('click', () => {
            const effectName = button.textContent.toLowerCase();
            applyEffect(effectName);
        })
    })

    function applyEffect(effectName){
        effectName = effectName.toLowerCase().replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
            return index === 0 ? word.toLowerCase() : word.toUpperCase();
        }).replace(/\s+/g, '');
        Caman("#canvas", image, function () {
            this.revert(false);
            this[effectName]().render();
        });
    }

    // Function to create slider
    function createSlider(filterName) {
        // Clear previous slider if any
        sliderContainer.innerHTML = '';

        // Create slider label
        const sliderLabel = document.createElement('label');
        sliderLabel.textContent = `Adjust ${filterName} Strength:`;
        sliderLabel.setAttribute('for', 'slider');

        // Create slider input
        const sliderInput = document.createElement('input');
        sliderInput.type = 'range';
        sliderInput.min = '0';
        sliderInput.max = '100';
        sliderInput.value = '0';
        sliderInput.classList.add('slider');
        sliderInput.id = 'slider';

        // Append slider label and input to slider container
        sliderContainer.appendChild(sliderLabel);
        sliderContainer.appendChild(sliderInput);
        sliderContainer.classList.add('show');

        // Add event listener to the slider
        sliderInput.addEventListener('input', () => {
            const sliderValue = sliderInput.value;
            applyFilter(filterName, sliderValue);
        });
    }

    // Apply filter using Caman
    function applyFilter(filterName, sliderValue) {
        // Check if the filter is already applied
        const index = appliedFilters.findIndex(item => item.filterName === filterName);
        if (index !== -1) {
            appliedFilters[index].sliderValue = sliderValue;
        } else {
            appliedFilters.push({ filterName, sliderValue });
        }

        // Apply all filters
        Caman("#canvas", image, function () {
            this.revert(false);
            appliedFilters.forEach(item => {
                this[item.filterName](parseInt(item.sliderValue));
            });
            this.render();
        });
    }

    // upload photo
    const upload = document.getElementById("upload-file");
    upload.addEventListener("change", () => {
        const file = upload.files[0];
        const reader = new FileReader();

        if (file) {
            fileName = file.name;
            reader.readAsDataURL(file);
        }

        reader.addEventListener("load", () => {
            image = new Image();
            image.src = reader.result;
            image.onload = function () {
                canvas.width = image.width;
                canvas.height = image.height;
                context.drawImage(image, 0, 0, image.width, image.height);
                canvas.removeAttribute("data-caman-id");
                // Reset applied filters
                appliedFilters = [];
            };
        }, false);
    });

    reset.addEventListener("click", (e) =>{
        Caman("#canvas", image, function () {
            this.revert();
        })
    });

    save.addEventListener('click', (e)=>{
        const fileExtension = fileName.slice(-4);
        let newFileName;
        if (fileExtension === '.jpg' || fileExtension === '.png') {
            newFileName = fileName.substring(0, fileName.length - 4) + '-edited.jpg';
        }
        download(canvas, newFileName)
    })

    function download(canvas, name) {
        let e;
        const link = document.createElement('a');
        link.download = name;
        link.href = canvas.toDataURL('image/jpeg', 0.8);
        e = new MouseEvent('click');
        link.dispatchEvent(e)
    }
});
