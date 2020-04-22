const speciesInput = document.querySelector("#species");
const genusInput = document.querySelector("#genus");
const familyInput = document.querySelector("#family");
const orderInput = document.querySelector("#order");
const phylumInput = document.querySelector("#phylum");
const kingdomInput = document.querySelector("#kingdom");
const authorshipInput = document.querySelector("#authorship");
const BASE_URL = "https://api.gbif.org/v1/species"

async function getTaxonInfo(e) {
    
    let inputValue = e.target.value;

    const response = await axios.get(`${BASE_URL}`, {
        params: {
            name: inputValue
        }
    })

    genusInput.value = response.data.results[0].genus
    familyInput.value = response.data.results[0].family
    orderInput.value = response.data.results[0].order
    phylumInput.value = response.data.results[0].phylum
    kingdomInput.value = response.data.results[0].kingdom
    authorshipInput.value = response.data.results[0].authorship

    console.log("Bingo!")
}

function debounced(delay, fn) {
    let timerId;
    return function (...args) {
        if (timerId) {
            clearTimeout(timerId);
        }
        timerId = setTimeout(() =>{
            fn(...args);
            timerId = null;
        }, delay)
    }
}


speciesInput.addEventListener('input', debounced(500, getTaxonInfo));
