import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from flask import Flask, render_template, request, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Email configuration
smtp_server = "smtp.gmail.com"  # Example for Gmail
smtp_port = 587  # Gmail SMTP port
email_username = "yasir.codeblue@gmail.com"
email_password = "xmyf deht uvqj pbur"  # Use app password for Gmail

# Function to send emails
def send_email(recipient_name, recipient_email, attachment_path):
    # Create message object instance
    msg = MIMEMultipart()
    msg["From"] = email_username
    msg["To"] = recipient_email
    msg["Subject"] = "Your Unique Attachment"

    # Email body text
    body = f"Dear {recipient_name},\n\nPlease find your unique attachment.\n\nBest regards,\nYour Name"
    msg.attach(MIMEText(body, "plain"))

    # Attach the unique file
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename={os.path.basename(attachment_path)}',
            )
            msg.attach(part)
    except Exception as e:
        print(f"Could not attach {attachment_path}: {e}")
        return False

    # Create a SMTP session
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS for security
        server.login(email_username, email_password)
        server.sendmail(email_username, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False

# Route for form (file upload)
@app.route('/', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith('.csv'):
            # Save file temporarily
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            # Read the CSV file
            try:
                df = pd.read_csv(filepath)
            except Exception as e:
                return jsonify({"error": f"Error reading CSV: {e}"}), 400

            # Send emails to each recipient
            for index, row in df.iterrows():
                recipient_name = row.get("Recipient Name")
                recipient_email = row.get("Email Address")
                attachment_path = row.get("Attachment Path")

                if recipient_name and recipient_email and attachment_path:
                    email_sent = send_email(recipient_name, recipient_email, attachment_path)
                    if not email_sent:
                        return jsonify({"error": f"Failed to send email to {recipient_email}"}), 500

            return jsonify({"message": "Emails sent successfully!"}), 200

    # If it's a GET request, render the form
    return render_template('upload_form.html')

if __name__ == '__main__':
    # Create uploads directory if not exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    app.run(debug=True)
