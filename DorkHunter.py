import argparse
from googlesearch import search
import sys
import time
import requests
import smtplib
import logging
import json
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Colors:
    RED = "\33[91m"
    BLUE = "\33[94m"
    GREEN = "\33[92m"
    RESET = "\033[0m"

def print_colored(text, color, end="\n", delay=0.0):
    """Prints text in a given color with an optional delay between each character."""
    for char in text:
        print(color + char + Colors.RESET, end="", flush=True)
        time.sleep(delay)
    print(end=end)

def save_to_file(data, filename, file_format):
    """Saves the provided data to a specified file in the given format."""
    if file_format == 'txt':
        with open(f"{filename}.txt", "a") as file:
            file.write(data + "\n")
    elif file_format == 'csv':
        with open(f"{filename}.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data])
    elif file_format == 'json':
        with open(f"{filename}.json", "a") as file:
            json.dump(data, file)
            file.write("\n")
    elif file_format == 'html':
        with open(f"{filename}.html", "a") as file:
            file.write(data + "<br>\n")

def send_email(receiver_email, smtp_server, smtp_port, smtp_user, smtp_pass, subject, message):
    """Sends an email using SMTP."""
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server.sendmail(smtp_user, receiver_email, msg.as_string())
        print("[+] Email sent successfully.")
    except Exception as e:
        print(f"[!] Failed to send email: {str(e)}")
    finally:
        server.quit()

def google_dork_search(args):
    """Main function to perform Google Dork search based on the provided arguments."""
    decorative_line = "\n" + "  " + "»" * 78 + "\n"
    developer_name = "D E V E L O P E D  B Y  K U N A L  N A M D A S"

    total_width = len(decorative_line.strip())
    spaces = " " * ((total_width - len(developer_name)) // 2)

    print(decorative_line, Colors.GREEN)
    print(spaces + developer_name, Colors.GREEN)
    # print(decorative_line, Colors.GREEN)

    logging.basicConfig(filename='dorking.log', level=logging.INFO)
    logging.info('Script started')

    dorks = []
    if args.dork:
        dorks.append(args.dork)
    if args.dorks_file:
        with open(args.dorks_file, 'r') as file:
            dorks.extend(file.read().splitlines())

    if not dorks:
        print_colored("[!] No dork query provided.", Colors.RED)
        logging.error('No dork query provided')
        sys.exit(1)

    if args.save:
        filename = args.save
        file_format = args.format
        # print(decorative_line)
    else:
        filename = None
        file_format = None
        # print("[!] Saving is skipped...")
        # print(decorative_line)

    try:
        for dork in dorks:
            if args.domain:
                dork += f" site:{args.domain}"
            print(decorative_line, Colors.GREEN)
            print_colored(f"[+] Searching for: {dork}", Colors.BLUE)
            logging.info(f'Searching for: {dork}')
            retries = 3
            while retries > 0:
                try:
                    for idx, result in enumerate(search(dork, num=args.number, stop=args.number, pause=2, user_agent=args.user_agent), start=1):
                        output = f"[+] {idx}. {result}"
                        print(output)
                        logging.info(output)
                        if filename:
                            if file_format == 'html':
                                save_to_file(f"<p>{output}</p>", filename, file_format)
                            else:
                                save_to_file(result, filename, file_format)
                        if args.verbose:
                            print(f"[*] Verbose: Retrieved {result}")
                        time.sleep(0.1)
                    break
                except Exception as e:
                    retries -= 1
                    logging.error(f'Error: {e}. Retries left: {retries}')
                    time.sleep(2)
            else:
                print_colored(f"\n[!] Failed to retrieve results for: {dork}", Colors.RED)
                logging.error(f'Failed to retrieve results for: {dork}')

        if args.email:
            subject = f"Google Dork Search Results - {dork}"
            message = f"Hello,\n\nHere are the search results for the Google Dork: {dork}\n\n"
            if filename:
                if file_format == 'txt':
                    with open(f"{filename}.txt", "r") as file:
                        message += file.read()
                elif file_format == 'csv':
                    with open(f"{filename}.csv", "r") as file:
                        message += file.read()
                elif file_format == 'json':
                    with open(f"{filename}.json", "r") as file:
                        message += file.read()
                elif file_format == 'html':
                    with open(f"{filename}.html", "r") as file:
                        message += file.read()
            send_email(args.email, args.smtp_server, args.smtp_port, args.smtp_user, args.smtp_pass, subject, message)

    except KeyboardInterrupt:
        print_colored("\n[!] User interruption detected.", Colors.RED)
        logging.warning('User interruption detected')
    except Exception as e:
        print_colored(f"\n[!] Error: {str(e)}", Colors.RED)
        logging.error(f'Error: {e}')
    finally:
        print(decorative_line, Colors.GREEN)
        print_colored("Google Dork Finder v3.0", Colors.GREEN, delay=0.002)
        print("[•] Done. Exiting...")
        logging.info('Script finished')
        sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Google Dork Finder")
    parser.add_argument("--dork", type=str, help="Google dork query to search")
    parser.add_argument("--dorks_file", type=str, help="File containing multiple dork queries")
    parser.add_argument("--domain", type=str, help="Specific domain to search within")
    parser.add_argument("--number", type=int, default=10, help="Number of search results to display")
    parser.add_argument("--save", type=str, help="File name to save the results")
    parser.add_argument("--format", type=str, choices=['txt', 'csv', 'json', 'html'], default='txt', help="Format to save the results (txt, csv, json, html)")
    parser.add_argument("--email", type=str, help="Email address to send results")
    parser.add_argument("--smtp_server", type=str, help="SMTP server for sending emails")
    parser.add_argument("--smtp_port", type=int, default=587, help="SMTP server port")
    parser.add_argument("--smtp_user", type=str, help="SMTP username (email address)")
    parser.add_argument("--smtp_pass", type=str, help="SMTP password or app-specific password")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument("--user_agent", type=str, default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", help="Custom User-Agent")

    args = parser.parse_args()

    google_dork_search(args)

if __name__ == "__main__":
    main()
