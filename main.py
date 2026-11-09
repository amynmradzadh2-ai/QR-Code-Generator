
from datetime import datetime
from pathlib import Path
import re
import qrcode
from qrcode.constants import ERROR_CORRECT_M


OUTPUT_DIR = Path("generated_qr")


def safe_filename(value):
    value = value.strip().lower()
    value = re.sub(r"[^\w-]+", "_", value)
    return value.strip("_")[:40] or "qr_code"


def save_qr(data, label):
    if not data.strip():
        raise ValueError("QR content cannot be empty.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename(label)}_{timestamp}.png"

    output_path = OUTPUT_DIR / filename
    image.save(output_path)

    print(f"\nQR code saved: {output_path.resolve()}")

    return output_path


def escape_vcard(value):
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def escape_wifi(value):
    for character in ("\\", ";", ",", ":", '"'):
        value = value.replace(character, "\\" + character)

    return value


def create_text_qr():
    content = input("Enter a link or text: ").strip()

    if not content:
        print("Content cannot be empty.")
        return

    save_qr(content, "text_or_link")


def create_contact_qr():
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    phone = input("Phone number (optional): ").strip()
    email = input("Email address (optional): ").strip()

    if not first_name and not last_name:
        print("Please enter a name.")
        return

    if not phone and not email:
        print("Enter at least a phone number or email.")
        return

    full_name = " ".join(
        part for part in (first_name, last_name) if part
    )

    card = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape_vcard(last_name)};{escape_vcard(first_name)};;;",
        f"FN:{escape_vcard(full_name)}"
    ]

    if phone:
        card.append(f"TEL;TYPE=CELL:{escape_vcard(phone)}")

    if email:
        card.append(f"EMAIL:{escape_vcard(email)}")

    card.append("END:VCARD")

    vcard = "\r\n".join(card) + "\r\n"

    save_qr(vcard, "contact_card")


def create_wifi_qr():
    ssid = input("Wi-Fi name: ").strip()

    if not ssid:
        print("Wi-Fi name cannot be empty.")
        return

    print("\nSecurity type:")
    print("1. WPA / WPA2 / WPA3")
    print("2. WEP")
    print("3. Open network")

    choice = input("Choose security type: ").strip()

    security_types = {
        "1": "WPA",
        "2": "WEP",
        "3": "nopass"
    }

    if choice not in security_types:
        print("Invalid security type.")
        return

    security = security_types[choice]
    password = ""

    if security != "nopass":
        password = input("Wi-Fi password: ")

        if not password:
            print("Password cannot be empty.")
            return

        if security == "WPA" and len(password) < 8:
            print("Warning: WPA passwords are usually at least 8 characters.")

    wifi = (
        f"WIFI:T:{security};"
        f"S:{escape_wifi(ssid)};"
        f"P:{escape_wifi(password)};;"
    )

    save_qr(wifi, "wifi")


def show_menu():
    print("\n" + "=" * 34)
    print("       QR CODE GENERATOR")
    print("=" * 34)

    print("1. Link or Text")
    print("2. Contact Card")
    print("3. Wi-Fi")
    print("4. Exit")

    print("-" * 34)


def main():
    actions = {
        "1": create_text_qr,
        "2": create_contact_qr,
        "3": create_wifi_qr
    }

    while True:
        try:
            show_menu()

            choice = input("Choose an option (1-4): ").strip()

            if choice == "4":
                print("Goodbye!")
                break

            action = actions.get(choice)

            if action is None:
                print("Invalid choice. Try again.")
                continue

            try:
                action()

            except (ValueError, OSError) as error:
                print(f"Error: {error}")

        except (KeyboardInterrupt, EOFError):
            print("\nProgram closed.")
            break


if __name__ == "__main__":
    main()
