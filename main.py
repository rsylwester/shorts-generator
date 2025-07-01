import gradio as gr
import os
import threading
import logging
from src.generators.video_generator import VideoGenerator
from src.utils.database import QuoteDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state for generation
is_generating = False
generation_lock = threading.Lock()

def upload_csv(csv_file):
    """Upload CSV file with quotes."""
    if csv_file is None:
        return "❌ Nie wybrano pliku CSV"
    
    try:
        db = QuoteDatabase()
        added_count = db.upload_csv(csv_file.name)
        stats = db.get_stats()
        
        return f"✅ Dodano {added_count} nowych cytatów. Łącznie w bazie: {stats['total']} cytatów ({stats['unused']} nieużytych)"
    
    except Exception as e:
        return f"❌ Błąd podczas wczytywania CSV: {str(e)}"

def get_database_stats():
    """Get current database statistics."""
    try:
        db = QuoteDatabase()
        stats = db.get_stats()
        return f"📊 Baza cytatów: {stats['total']} łącznie ({stats['unused']} nieużytych, {stats['used']} użytych)"
    except Exception as e:
        return f"❌ Błąd: {str(e)}"

def generate_video():
    """Generate video from random quote."""
    global is_generating
    
    logger.info("Video generation requested")
    
    with generation_lock:
        if is_generating:
            logger.warning("Video generation already in progress")
            return None, "⚠️ Trwa już generowanie wideo. Proszę poczekać...", "", "", ""
        
        is_generating = True
    
    try:
        # Get random quote
        logger.info("Getting random quote from database")
        db = QuoteDatabase()
        quote = db.get_random_unused_quote()
        
        if quote is None:
            logger.warning("No quotes available in database")
            return None, "❌ Brak cytatów w bazie. Proszę wgrać plik CSV z cytatami.", "", "", ""
        
        logger.info(f"Selected quote: {quote.quote[:50]}... by {quote.author}")
        
        # Generate video
        logger.info("Starting video generation")
        generator = VideoGenerator()
        generated_video = generator.create_video(quote)
        
        # Mark quote as used
        logger.info("Marking quote as used")
        db.mark_quote_used(quote.id)
        
        # Update stats
        stats = db.get_stats()
        status_message = f"✅ Wideo wygenerowane w {generated_video.generation_time:.1f}s. Pozostało nieużytych cytatów: {stats['unused']}"
        logger.info(status_message)
        
        # Convert file path to proper format for Gradio
        video_path = os.path.abspath(generated_video.file_path)
        logger.info(f"Returning video path: {video_path}")
        
        return (
            video_path,
            status_message,
            quote.social_media_post,
            get_database_stats(),
            f"📁 Plik wideo: {video_path}"
        )
        
    except Exception as e:
        error_msg = f"❌ Błąd podczas generowania: {str(e)}"
        logger.error(f"Video generation failed: {str(e)}")
        return None, error_msg, "", get_database_stats(), ""
    
    finally:
        with generation_lock:
            is_generating = False
        logger.info("Video generation process completed")

def copy_social_media_text(text):
    """Return text for copying."""
    if text:
        return gr.update(value="✅ Tekst skopiowany do schowka!", visible=True)
    return gr.update(value="❌ Brak tekstu do skopiowania", visible=True)

def main():
    # Custom CSS for dark theme
    css = """
    .gradio-container {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    .gr-button-primary {
        background: linear-gradient(90deg, #7B2CBF, #9D4EDD) !important;
        border: none !important;
    }
    .gr-button-primary:hover {
        background: linear-gradient(90deg, #6A1A9A, #8B3CBB) !important;
    }
    """
    
    with gr.Blocks(title="ShortsGenerator MVP", css=css, theme=gr.themes.Soft(primary_hue="purple")) as app:
        gr.Markdown("# 📱 ShortsGenerator MVP")
        gr.Markdown("Automatyczne generowanie 12-sekundowych filmów z cytatami medytacyjnymi")
        
        with gr.Tabs(selected=1):
            # Tab 1: Upload CSV
            with gr.TabItem("📁 Wgrywanie Cytatów"):
                gr.Markdown("### Wgraj plik CSV z cytatami")
                gr.Markdown("**Format CSV:** ID, QUOTE, AUTHOR, REFLECTION, SOCIAL_MEDIA_POST, STATUS")
                
                with gr.Row():
                    with gr.Column():
                        csv_file = gr.File(
                            label="Wybierz plik CSV",
                            file_types=[".csv"],
                            file_count="single"
                        )
                        upload_btn = gr.Button("📤 Wgraj Cytaty", variant="primary")
                    
                    with gr.Column():
                        upload_status = gr.Textbox(
                            label="Status wgrywania",
                            interactive=False,
                            lines=3
                        )
                
                upload_btn.click(
                    fn=upload_csv,
                    inputs=[csv_file],
                    outputs=[upload_status]
                )
            
            # Tab 2: Generate Video
            with gr.TabItem("🎬 Generowanie Wideo"):
                gr.Markdown("### Generuj wideo z losowym cytatem")
                
                with gr.Row():
                    with gr.Column():
                        db_stats = gr.Textbox(
                            label="Stan bazy danych",
                            interactive=False,
                            value=get_database_stats()
                        )
                        
                        generate_btn = gr.Button("🎬 Generuj Wideo", variant="primary", size="lg")
                        
                        generation_status = gr.Textbox(
                            label="Status generowania",
                            interactive=False,
                            lines=2
                        )
                    
                    with gr.Column():
                        video_output = gr.Video(
                            label="Wygenerowane wideo",
                            height=400,
                            show_download_button=True,
                            show_share_button=False
                        )
                        
                        download_info = gr.Textbox(
                            label="Link do pobrania",
                            interactive=False,
                            visible=True,
                            placeholder="Po wygenerowaniu wideo pojawi się tutaj ścieżka do pliku..."
                        )
                
                with gr.Row():
                    with gr.Column():
                        social_media_text = gr.Textbox(
                            label="Tekst do social media",
                            interactive=False,
                            lines=4,
                            placeholder="Po wygenerowaniu wideo pojawi się tutaj gotowy tekst do publikacji..."
                        )
                        
                        copy_btn = gr.Button("📋 Kopiuj tekst", variant="secondary")
                        copy_status = gr.Textbox(
                            label="Status kopiowania",
                            interactive=False,
                            visible=True
                        )
                
                # Event handlers
                generate_btn.click(
                    fn=generate_video,
                    outputs=[video_output, generation_status, social_media_text, db_stats, download_info]
                )
                
                copy_btn.click(
                    fn=copy_social_media_text,
                    inputs=[social_media_text],
                    outputs=[copy_status]
                ).then(
                    fn=None,
                    inputs=[social_media_text],
                    outputs=[],
                    js="(text) => navigator.clipboard.writeText(text)"
                )
                
                # Auto-refresh stats when page loads
                app.load(
                    fn=get_database_stats,
                    outputs=[db_stats]
                )
        
        gr.Markdown("---")
        gr.Markdown("*ShortsGenerator MVP - Profesjonalne wideo w 1-3 minuty*")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()