import cloudinary.uploader

cloudinary.config(
    cloud_name = "dx9vdtrxz",
    api_key = "393536875249411",
    api_secret = "jJ4FwQKz8FUP7VPLVAlYKt09588",
)


def upload_profile_picture(file, file_name, **options):
    uploaded_image = cloudinary.uploader.upload(
        file,
        public_id = file_name, 
        crop = 'limit',
        eager = [
            {'crop': 'thumb', 'gravity': 'face',},

        ],
        tags = ['profile_pic'],
    )

    return uploaded_image

def add_image_description(file, file_name, **options):
    uploaded_image = cloudinary.uploader.upload(
        file,
        public_id = file_name, 
        crop = 'limit',
        eager = [
            {'crop': 'thumb',},

        ],
        tags = ['description_img'],
    )

    return uploaded_image