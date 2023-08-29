document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const imageForm = document.getElementById('imageForm');
    const userIdElement = document.getElementById('user-id');
    const userId = userIdElement.dataset.userId;

    let cropper;

    imageInput.addEventListener('change', function () {
        const file = imageInput.files[0];
        const reader = new FileReader();

        reader.onload = function (e) {
            imagePreview.src = e.target.result;

            if (file) {
                imagePreview.style.display = 'block'; // Отобразить imagePreview при выборе файла
            } else {
                imagePreview.style.display = 'none'; // Скрыть imagePreview, если файл не выбран
            }

            cropper = new Cropper(imagePreview, {
                aspectRatio: 1,
                viewMode: 1,
            });
        };

        reader.readAsDataURL(file);
    });

    imageForm.addEventListener('submit', function (event) {
        event.preventDefault();
        if (cropper) {
            cropper.getCroppedCanvas().toBlob(function (blob) {
                const formData = new FormData();
                formData.append('image', blob);

                fetch(`/avatar/${userId}`, {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        console.error("Произошла ошибка при обработке изображения.");
                    }
                });
            }, 'image/jpeg');
        }
    });
});
