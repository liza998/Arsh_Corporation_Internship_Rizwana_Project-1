
const dropArea = document.getElementById("drop-area");
const inputfile = document.getElementById("input-file");
const imageView = document.getElementById("image-view");

let selecedfile = null;

inputfile.addEventListener("change", uploadImage);

function uploadImage(){
    selecedfile = inputfile.files[0]
    imageView.textContent = "Image Uploaded ✔";
    imageView.style.border = "2px solid green";


}

dropArea.addEventListener("dragover", function (e) {
    e.preventDefault();
});

dropArea.addEventListener("drop", function (e) {
    e.preventDefault();

    selectedFile = e.dataTransfer.files[0];
    inputfile.files = e.dataTransfer.files;

    imageView.textContent = "Image Uploaded ✔";
    imageView.style.border = "2px solid green";
});


