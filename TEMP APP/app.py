"""
1stop Certificate Verification & QR Code Generator Web Application
Built with Streamlit and Pillow.
"""

import os
import io
import datetime
import streamlit as st
from PIL import Image

import certificate_generator as cg

# Page configuration
st.set_page_config(
    page_title="Verify Certificate | 1stop Keep Growing",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificates.db")
cg.init_db(DB_PATH)

# Detect Local IP for convenient mobile scanning over LAN/WiFi
LOCAL_IP = cg.get_local_ip()

# Custom CSS for exact styling matching the 1stop reference demo
st.markdown("""
<style>
    /* Import modern clean fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Header Navbar styling */
    .brand-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 20px;
        background: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        margin: -4rem -3rem 1.5rem -3rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .brand-logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
    }
    .brand-icon {
        background: #F58220;
        color: white;
        font-weight: 800;
        font-size: 20px;
        width: 36px;
        height: 38px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(245, 130, 32, 0.35);
    }
    .brand-text-block {
        display: flex;
        flex-direction: column;
    }
    .brand-title {
        color: #0E2F56;
        font-size: 26px;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .brand-slogan {
        color: #0E2F56;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-top: 3px;
    }
    .nav-hamburger {
        display: flex;
        flex-direction: column;
        gap: 5px;
        cursor: pointer;
        padding: 6px;
    }
    .hamburger-bar {
        width: 24px;
        height: 3px;
        background-color: #475569;
        border-radius: 2px;
    }

    /* Reference Title & Orange Accent */
    .page-header-box {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .main-verify-title {
        color: #1565C0;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    .accent-pill {
        width: 140px;
        height: 6px;
        background: #F58220;
        border-radius: 9999px;
        margin: 0 auto;
    }

    /* Verification Card - Styled like the screenshot */
    .verify-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 36px 32px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        border: 1px solid #EEF2F6;
        max-width: 580px;
        margin: 0 auto 30px auto;
    }

    .card-label {
        font-size: 17px;
        font-weight: 600;
        color: #334155;
        margin-bottom: 12px;
        text-align: center;
    }

    /* Button styling */
    div.stButton > button:first-child {
        background-color: #007BFF;
        color: white;
        font-size: 16px;
        font-weight: 700;
        padding: 10px 28px;
        border-radius: 10px;
        border: none;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.25);
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3;
        color: white;
        box-shadow: 0 6px 16px rgba(0, 123, 255, 0.35);
        transform: translateY(-1px);
    }

    /* Verified Certificate Banner */
    .verified-banner {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
        margin-bottom: 24px;
    }
    .verified-icon {
        font-size: 32px;
        background: rgba(255, 255, 255, 0.2);
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .verified-text-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -0.2px;
        margin: 0;
    }
    .verified-text-sub {
        font-size: 13px;
        opacity: 0.92;
        margin: 2px 0 0 0;
    }

    /* Certificate Detail Grid */
    .cert-details-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }
    .cert-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px dashed #E2E8F0;
    }
    .cert-row:last-child {
        border-bottom: none;
    }
    .cert-key {
        font-size: 14px;
        color: #64748B;
        font-weight: 500;
    }
    .cert-val {
        font-size: 15px;
        color: #0E2F56;
        font-weight: 700;
        text-align: right;
    }

    /* Footer Banner matching reference */
    .brand-footer {
        background: #0288D1;
        color: white;
        padding: 28px 24px;
        border-radius: 18px 18px 0 0;
        margin: 40px -3rem -4rem -3rem;
        box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.05);
    }
    .footer-content {
        max-width: 600px;
        margin: 0 auto;
        text-align: left;
    }
    .footer-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    .footer-desc {
        font-size: 13px;
        line-height: 1.6;
        color: #E0F2FE;
        margin: 0;
    }
    .whatsapp-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #25D366;
        color: white;
        font-size: 13px;
        font-weight: 700;
        padding: 8px 16px;
        border-radius: 20px;
        text-decoration: none;
        margin-top: 14px;
        box-shadow: 0 3px 8px rgba(37, 211, 102, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# Top Navigation Bar (Identical to 1stop mobile header)
st.markdown("""
<div class="brand-navbar">
    <div class="brand-logo-container">
        <div class="brand-icon">1</div>
        <div class="brand-text-block">
            <span class="brand-title">1stop</span>
            <span class="brand-slogan">Keep Growing</span>
        </div>
    </div>
    <div class="nav-hamburger" title="Navigation Menu">
        <div class="hamburger-bar"></div>
        <div class="hamburger-bar"></div>
        <div class="hamburger-bar"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check query params for QR Code Traceback: `?cert_id=...`
query_params = st.query_params
scanned_cert_id = query_params.get("cert_id", "").strip()

# Sidebar for App Settings & Network Guide
with st.sidebar:
    st.markdown("### ⚙️ QR Code Verification Settings")
    st.info("💡 **How QR Code Scanning Works:**\nWhen someone scans the QR code with their smartphone, their phone browser will open the verification URL encoded in the QR code.")
    
    st.markdown("#### Choose Base URL for QR Codes")
    url_mode = st.radio(
        "Host Connection Mode",
        [
            f"📱 Local WiFi / LAN Network (Recommended for Mobile Scanning)",
            f"💻 Localhost (Testing on this computer)",
            f"🌐 Custom Public Domain / Tunnel (e.g. ngrok / cloud)"
        ],
        index=0
    )

    if "Local WiFi" in url_mode:
        active_base_url = f"http://{LOCAL_IP}:8501"
        st.success(f"**Mobile Scan Base URL:**\n`{active_base_url}`\n\nEnsure your phone is connected to the same WiFi/Network.")
    elif "Localhost" in url_mode:
        active_base_url = "http://localhost:8501"
        st.caption("Works for browser testing on this local machine.")
    else:
        custom_input = st.text_input("Enter your public domain or ngrok URL", value=f"http://{LOCAL_IP}:8501")
        active_base_url = custom_input.strip()

    st.markdown("---")
    st.caption("1stop Certificate Authenticity & Traceback System")
    st.caption("Database: SQLite (`certificates.db`)")


# Main Tabs
tab_verify, tab_generate, tab_registry = st.tabs([
    "🔍 Verify Certificate", 
    "🎓 Generate Certificate & QR Code", 
    "📋 Certificate Registry"
])


# ==============================================================================
# TAB 1: VERIFY CERTIFICATE (Matches Reference Image & Handles QR Scan Traceback)
# ==============================================================================
with tab_verify:
    st.markdown("""
    <div class="page-header-box">
        <div class="main-verify-title">Verify Certificate</div>
        <div class="accent-pill"></div>
    </div>
    """, unsafe_allow_html=True)

    # If QR code was scanned and passed cert_id in URL
    if scanned_cert_id:
        st.toast(f"Traceback scan detected: {scanned_cert_id}", icon="⚡")
        cert_data = cg.get_certificate_by_id(scanned_cert_id, DB_PATH)
        
        if cert_data:
            # Verified Banner
            st.markdown(f"""
            <div class="verified-banner">
                <div class="verified-icon">✓</div>
                <div>
                    <div class="verified-text-title">OFFICIALLY VERIFIED & AUTHENTIC</div>
                    <div class="verified-text-sub">This certificate record has been traced back and authenticated via 1stop Registry.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Details Card
            st.markdown(f"""
            <div class="cert-details-card">
                <div class="cert-row">
                    <span class="cert-key">Student Name:</span>
                    <span class="cert-val">{cert_data['name']}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Course Title:</span>
                    <span class="cert-val">{cert_data['course']}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Certificate Verification ID:</span>
                    <span class="cert-val" style="color:#F58220;">{cert_data['id']}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Issue Date:</span>
                    <span class="cert-val">{cert_data['issue_date']}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Performance / Grade:</span>
                    <span class="cert-val">{cert_data.get('grade', 'Completed')}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Issuing Platform:</span>
                    <span class="cert-val">{cert_data['issuer']}</span>
                </div>
                <div class="cert-row">
                    <span class="cert-key">Authentication Status:</span>
                    <span class="cert-val" style="color:#10B981;">● Active & Verified</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # High-Resolution Certificate Preview
            st.markdown("#### 📜 Official Certificate of Completion")
            cert_img = cg.render_certificate_image(cert_data)
            st.image(cert_img, use_container_width=True, caption=f"1stop Official Certificate — ID: {cert_data['id']}")

            # Download Buttons
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                cert_bytes = cg.get_image_bytes(cert_img, "PNG")
                st.download_button(
                    label="📥 Download Certificate (PNG)",
                    data=cert_bytes,
                    file_name=f"1stop_Certificate_{cert_data['id']}.png",
                    mime="image/png",
                    use_container_width=True
                )
            with c_col2:
                # Button to clear scan query param
                if st.button("🔄 Verify Another Certificate", use_container_width=True):
                    st.query_params.clear()
                    st.rerun()

        else:
            st.error(f"❌ Certificate ID **{scanned_cert_id}** not found in the official registry.")
            if st.button("← Back to Search"):
                st.query_params.clear()
                st.rerun()

    else:
        # Standard Verification Screen matching the user's reference image
        with st.container():
            st.markdown('<div class="card-label">Enter Email address or Certificate ID</div>', unsafe_allow_html=True)
            
            search_input = st.text_input(
                label="Enter Email address or Certificate ID",
                placeholder="e.g. 1STOP-2026-DEMO01 or student@example.com",
                label_visibility="collapsed",
                key="manual_verify_input"
            )

            btn_verify = st.button("Verify", use_container_width=True, key="manual_verify_btn")

            if btn_verify:
                if not search_input.strip():
                    st.warning("⚠️ Please enter a Certificate ID or Email address to verify.")
                else:
                    results = cg.search_certificates(search_input, DB_PATH)
                    if results:
                        st.session_state["search_results"] = results
                    else:
                        st.session_state["search_results"] = []
                        st.error(f"❌ No verified certificate found matching '{search_input}'. Please check the ID or email.")

            # Display search results if any
            if "search_results" in st.session_state and st.session_state["search_results"]:
                found_certs = st.session_state["search_results"]
                st.success(f"✓ Found {len(found_certs)} verified certificate record(s)!")

                for cert in found_certs:
                    st.markdown(f"""
                    <div class="verified-banner" style="margin-top:20px;">
                        <div class="verified-icon">✓</div>
                        <div>
                            <div class="verified-text-title">CERTIFICATE AUTHENTICATED: {cert['id']}</div>
                            <div class="verified-text-sub">Issued to {cert['name']} for {cert['course']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="cert-details-card">
                        <div class="cert-row">
                            <span class="cert-key">Student Name:</span>
                            <span class="cert-val">{cert['name']}</span>
                        </div>
                        <div class="cert-row">
                            <span class="cert-key">Course:</span>
                            <span class="cert-val">{cert['course']}</span>
                        </div>
                        <div class="cert-row">
                            <span class="cert-key">Email:</span>
                            <span class="cert-val">{cert.get('email') or 'N/A'}</span>
                        </div>
                        <div class="cert-row">
                            <span class="cert-key">Issue Date:</span>
                            <span class="cert-val">{cert['issue_date']}</span>
                        </div>
                        <div class="cert-row">
                            <span class="cert-key">Verification Traceback Link:</span>
                            <span class="cert-val"><a href="{cert['qr_data']}" target="_blank">Direct Link</a></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    cert_img = cg.render_certificate_image(cert)
                    st.image(cert_img, use_container_width=True)

                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        img_bytes = cg.get_image_bytes(cert_img, "PNG")
                        st.download_button(
                            label="📥 Download Certificate",
                            data=img_bytes,
                            file_name=f"Certificate_{cert['id']}.png",
                            mime="image/png",
                            key=f"dl_cert_{cert['id']}",
                            use_container_width=True
                        )
                    with col_dl2:
                        qr_img = cg.generate_qr_code(cert["qr_data"])
                        qr_bytes = cg.get_image_bytes(qr_img, "PNG")
                        st.download_button(
                            label="📱 Download QR Code",
                            data=qr_bytes,
                            file_name=f"QRCode_{cert['id']}.png",
                            mime="image/png",
                            key=f"dl_qr_{cert['id']}",
                            use_container_width=True
                        )


# ==============================================================================
# TAB 2: GENERATE CERTIFICATE & QR CODE
# ==============================================================================
with tab_generate:
    st.markdown("""
    <div class="page-header-box">
        <div class="main-verify-title" style="color:#0E2F56;">Generate Certificate & QR Code</div>
        <div class="accent-pill"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("Fill in the student details below to generate a verified certificate with an interactive QR code.")

    with st.form("generate_certificate_form"):
        col1, col2 = st.columns(2)
        with col1:
            input_name = st.text_input("Student Full Name *", placeholder="e.g. Padagala Sathvik")
            input_email = st.text_input("Student Email Address", placeholder="e.g. sathvik@example.com")
            input_grade = st.selectbox(
                "Performance / Distinction",
                [
                    "Grade A+ (Distinction & Honors)",
                    "Grade A (Outstanding Performance)",
                    "Completed with Excellence",
                    "Certified Practitioner",
                    "Passed with Merit"
                ]
            )
        with col2:
            input_course = st.text_input("Course Name *", placeholder="e.g. Full Stack Web Development & AI")
            input_date = st.date_input("Issue Date", value=datetime.date.today())
            input_issuer = st.text_input("Issuing Authority", value="1stop Keep Growing")

        # Custom ID or Auto-generated
        use_custom_id = st.checkbox("Specify custom Certificate ID (optional)")
        custom_id_val = ""
        if use_custom_id:
            custom_id_val = st.text_input("Custom Certificate ID", placeholder="e.g. 1STOP-2026-CUSTOM101")

        st.caption(f"🔗 **Encoded Verification URL in QR:** `{active_base_url}/?cert_id=<AUTOGENERATED_ID>`")
        
        submit_btn = st.form_submit_button("✨ Generate Certificate & QR Code", use_container_width=True)

    if submit_btn:
        if not input_name.strip() or not input_course.strip():
            st.error("⚠️ Please provide both the **Student Name** and the **Course Name**.")
        else:
            formatted_date = input_date.strftime("%B %d, %Y")
            new_cert = cg.add_certificate(
                name=input_name,
                course=input_course,
                email=input_email,
                issue_date=formatted_date,
                grade=input_grade,
                issuer=input_issuer,
                base_url=active_base_url,
                custom_id=custom_id_val if use_custom_id else None,
                db_path=DB_PATH
            )

            st.success(f"🎉 Certificate successfully created for **{new_cert['name']}**!")
            
            # Display Generated Results
            st.markdown("### 📱 Generated QR Code & Verification Traceback")
            
            col_qr, col_info = st.columns([1, 1.5])
            
            with col_qr:
                qr_pil = cg.generate_qr_code(new_cert["qr_data"], box_size=8, border=3)
                st.image(qr_pil, caption=f"Scan to Verify — ID: {new_cert['id']}", use_container_width=True)
                
                qr_bytes = cg.get_image_bytes(qr_pil, "PNG")
                st.download_button(
                    label="📥 Download QR Code (PNG)",
                    data=qr_bytes,
                    file_name=f"QR_{new_cert['id']}.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col_info:
                st.markdown(f"""
                **Certificate ID:** `{new_cert['id']}`  
                **Student:** **{new_cert['name']}**  
                **Course:** **{new_cert['course']}**  
                **Issue Date:** {new_cert['issue_date']}  
                **Grade:** {new_cert['grade']}  
                
                **Encoded Verification Traceback URL:**  
                [{new_cert['qr_data']}]({new_cert['qr_data']})
                """)

                # Quick Simulation Button
                st.markdown("---")
                st.markdown("**Test Scan Traceback Right Now:**")
                if st.button("🚀 Simulate Scanning QR Code (Open Verification View)", key="sim_scan_btn", use_container_width=True):
                    st.query_params["cert_id"] = new_cert["id"]
                    st.rerun()

            # Render Full Certificate Image
            st.markdown("---")
            st.markdown("### 📜 Official Certificate Preview (Embedded with QR Code)")
            cert_pil = cg.render_certificate_image(new_cert)
            st.image(cert_pil, use_container_width=True)

            cert_bytes = cg.get_image_bytes(cert_pil, "PNG")
            st.download_button(
                label="📥 Download Official Certificate (High Resolution PNG)",
                data=cert_bytes,
                file_name=f"Certificate_{new_cert['id']}.png",
                mime="image/png",
                use_container_width=True
            )


# ==============================================================================
# TAB 3: CERTIFICATE REGISTRY & DATABASE
# ==============================================================================
with tab_registry:
    st.markdown("""
    <div class="page-header-box">
        <div class="main-verify-title" style="color:#0E2F56;">Certificate Registry</div>
        <div class="accent-pill"></div>
    </div>
    """, unsafe_allow_html=True)

    all_certs = cg.get_all_certificates(DB_PATH)
    st.markdown(f"**Total Registered Certificates:** `{len(all_certs)}`")

    if all_certs:
        for c in all_certs:
            with st.expander(f"🎓 {c['id']} — {c['name']} ({c['course']})", expanded=False):
                r1, r2 = st.columns([2, 1])
                with r1:
                    st.write(f"**Student:** {c['name']}")
                    st.write(f"**Course:** {c['course']}")
                    st.write(f"**Email:** {c.get('email') or 'N/A'}")
                    st.write(f"**Date:** {c['issue_date']}")
                    st.write(f"**Traceback URL:** [{c['qr_data']}]({c['qr_data']})")
                with r2:
                    reg_qr = cg.generate_qr_code(c["qr_data"], box_size=4)
                    st.image(reg_qr, width=130)
                
                # Action buttons
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button(f"🔍 Verify Record", key=f"verify_reg_{c['id']}", use_container_width=True):
                        st.query_params["cert_id"] = c["id"]
                        st.rerun()
                with b_col2:
                    c_img = cg.render_certificate_image(c)
                    c_bytes = cg.get_image_bytes(c_img, "PNG")
                    st.download_button(
                        label="📥 Download Certificate",
                        data=c_bytes,
                        file_name=f"Certificate_{c['id']}.png",
                        mime="image/png",
                        key=f"dl_reg_{c['id']}",
                        use_container_width=True
                    )
    else:
        st.info("No certificates generated yet. Go to the 'Generate Certificate' tab to create one!")


# ==============================================================================
# FOOTER BANNER (Matches the 1stop banner at bottom of reference image)
# ==============================================================================
st.markdown("""
<div class="brand-footer">
    <div class="footer-content">
        <div class="footer-brand">
            <div class="brand-icon" style="width:28px; height:30px; font-size:16px;">1</div>
            <div class="brand-text-block">
                <span style="font-size:20px; font-weight:800; color:white; line-height:1;">1stop</span>
                <span style="font-size:9px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:0.5px;">Keep Growing</span>
            </div>
        </div>
        <p class="footer-desc">
            One Stop Tech is a strong platform with immense potential for students from anywhere and anytime to access cutting-edge Mentorship and Certification.
        </p>
        <a href="https://wa.me/" target="_blank" class="whatsapp-badge">
            💬 Chat on WhatsApp Support
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
