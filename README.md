# OSU!Web

**Osu!web** is a community website for **Osu!** or any rhythm-game players where users can sign up, upload and preview beatmaps, save favourites, and participate in discussions. It provides a simple, modern platform for discovering and sharing beatmaps with the community.

## Installation/Setup

### Download

Use the command below at your selected directory to first download program

```bash
git clone https://github.com/SXSreax/Osu-Web.git
```

### Creating a Python Virtual Environment

1. Open a terminal **(use cmd)** in the project's **root directory** (the same directory containing `requirements.txt`).
2. Create a Python virtual environment using the codes (**YOUR VENV SHOULD BE AT ROOT DIRECTORY**):

```cmd
python -m venv .venv
```

3. Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

4. Install the required packages from **requirements.txt**:

```cmd
pip install -r requirements.txt
```

5. The virtual environment is now created and should be ready.

### .Secrets

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
