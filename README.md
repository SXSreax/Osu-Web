<p align="center"> <img src="app/static/images/default_banner.png" alt="OSU!Web Banner" width="900"> </p>

<h1 style="text-align: center; font-weight: 700; color: #ff66aa;">OSU!Web</h1>

<p align="center"> Osu!Web is a self-developed community website for Osu! or any rhythm-game players where users can sign up, upload and preview beatmaps, save favourites, and participate in discussions. It provides a simple, modern platform for discovering and sharing beatmaps with the community. </p>

<h2 align="center"> Build With </h2>

<p align="center">
This section list any major **frameworks/libraries** used to make this program possible.
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,sqlite,js,html,css,git,github,vscode" />
</p>

## Installation/Setup

### Download

Use the command below at your selected directory to first download program

```bash
git clone https://github.com/SXSreax/Osu-Web.git
```

### Creating a Python Virtual Environment

1. Open a terminal **(use cmd)** in the project's **root directory** (the same directory containing `requirements.txt`).
2. Use python download from the python official page --> **[Python](https://www.python.org/)** **OR** Create a Python virtual environment using the codes (**YOUR VENV SHOULD BE AT ROOT DIRECTORY**):

3. Create venv folder **(optional)**:

```cmd
python -m venv .venv
```

4. Activate the virtual environment **(optional)**:

```cmd
.venv\Scripts\activate
```

5. Install the required packages from **requirements.txt**:

```cmd
pip install -r requirements.txt
```

6. The virtual environment is now created and should be ready.

### .Secrets

<p style="display: flex; align-items: center; gap: 8px;">
  <img src="app/static/images/key.svg" alt="Key" width="20" height="20">
  <strong style="font-size: 20px;">.secrets</strong>
</p>

This project requires a `.secrets` file to run. Regardless of how you obtain the file, **rename it to `.secrets`** before placing it in the project's **root directory** (where run.py is).

You can obtain the file in one of the following ways:

1. Request a copy from the owner of this project.
2. Create your own

### Create .Secrets

1. Create a file name ".secrets" and place it in the project's root directory (where run.py is)
2. In the `.secrets` file, you will need the following keys/api:
   - `OSU_CLIENT_ID=`
   - `OSU_CLIENT_SECRET=`
   - `KEY=`
   - `MAIL_USERNAME=`
   - `MAIL_PASSWORD=`
   - `MAIL_DEFAULT_SENDER=`
3. To get the `OSU_CLIENT_ID=` and `OSU_CLIENT_SECRET=`:
   - Register an osu! account at **[OSU OFFICAL](https://osu.ppy.sh/)**.
   - Press the **avatar icon** and go to the **Settings** page.
   - Scroll down and find the **OAuth** section.
   - Press **New OAuth Application**.
   - Copy and paste the **Client ID** (should be all numbers) and the **Client Secret** (Mixed)
4. To get the `KEY=` (its just a 32base code for pyotp):
   - use a python file with this code below

   ```python
   import pyotp

   key = pyotp.random_base32()
   print("key")
   ```

- Copy and paste the printed key from the terminal

5. To get the `MAIL_USERNAME=` and `MAIL_DEFAULT_SENDER=`:
   - **IMPORTANT:** Must use gmail account
   - Create a new gmail account (or you can use your own) at **[Create Gmail](https://support.google.com/mail/answer/56256?hl=en)**
   - Then copy and paste your email (e.g. example@extension.domain) the same both in `MAIL_USERNAME=` and `MAIL_DEFAULT_SENDER=`

6. To get the `MAIL_PASSWORD=`:
   - Go to your new **[Google Account Page](https://myaccount.google.com/)**
   - Go to **Security & sign-in**
   - Go to **2-Step Verification** and enable it
   - Then go back and search for **app password**
   - Create then copy and paste the password (it should be 16 characters)

7. The `.secrets` should be ready

## Usage

**_<span style="color: gold; font-size: 25;">Congratulations</span>_** (If you follow the steps)

The program should run now

To run the program:

```cmd
python run.py
```

### User **can**:

- 🏠 Visit the homepage and learn about OSU!Web.
- 🎵 Browse available osu!mania beatmaps.
- 🔎 Explore and discover new beatmaps.
- 📄 View detailed beatmap information.
- 🔊 Preview beatmap audio.
- ⬇️ Download beatmaps.
- ❤️ Like beatmaps and discussions.
- ⭐ Save beatmaps and discussions to their favourites.
- 📤 Upload their own beatmaps.
- 👤 Create and manage their own profile.
- 🖼️ Change their avatar and banner.
- 💬 Create community discussions.
- 💭 Comment on existing discussions.
- 👀 View other users' uploaded content.
- 🚪 Log out of their account.
