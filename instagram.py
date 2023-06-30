import instaloader


def get_posts(username):
    loader = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        for post in profile.get_posts():
            if post.is_video:
                loader.download_post(post, target=username)
                print(f"Se ha descargado el último video de {username}")
                break
            else:
                print(f"El último post de {username} no es un video.")

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"El perfil '{username}' no existe.")


get_posts('shakira')