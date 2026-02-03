# Future Improvements & Todo

## WhatsApp Integration
- [ ] **Offline Handling Robustness:** Ensure messages received when the PC/Service was off are reliably processed upon startup. (Currently implemented via history sync + initial buffer sweep, but needs verification).
- [ ] **Media Downloads:**
    - [ ] **Images:** Improve handling, downloading, and potential OCR/Vision analysis for images.
    - [ ] **PDFs:** Verify and improve PDF download reliability and text extraction.
    - [ ] **Other Formats:** Handle videos/audio notes better.

## General
- [ ] **Error Handling:** Add more timeouts to external API calls (Gemini, Web requests) to prevent thread hangs.
- [ ] **Buffer Management:** Ensure `inbox_buffer` never gets clogged with corrupt files.
