import cloudinary.uploader

cloudinary.config(
    cloud_name = "dx9vdtrxz",
    api_key = "393536875249411",
    api_secret = "jJ4FwQKz8FUP7VPLVAlYKt09588",
)


def upload_image_option(file, file_name, **options):
    uploaded_image = cloudinary.uploader.upload(
        file,
        public_id = file_name, 
        crop = 'limit',
        eager = [
            {'crop': 'thumb'},

        ],
        tags = ['profile_pic'],
    )

    return uploaded_image