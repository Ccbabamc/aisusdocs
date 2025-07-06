# USTravelDocs Bot

A comprehensive, robust Playwright-based automation bot for ustraveldocs.com that can navigate through the complete visa application flow including login, captcha solving, security questions, and appointment rescheduling.

## Features

- **Complete Flow Automation**: From visa entry page to appointment rescheduling interface
- **Anti-Bot Bypass**: Advanced techniques to avoid detection
- **Proxy Support**: Configurable proxy settings with authentication
- **Captcha Solving**: Integration with 2captcha service
- **Security Questions**: Intelligent matching and answering of Turkish security questions
- **Human-like Behavior**: Random delays, mouse movements, and typing patterns
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Screenshot Capture**: Automatic screenshots for debugging
- **Session Management**: Persistent session storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ccbabamc/aisusdocs.git
cd aisusdocs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Configuration

Edit `config.json` to configure your settings:

```json
{
  "config": {
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "captcha_api_key": "YOUR_2CAPTCHA_API_KEY",
    "headless": false,
    "save_screenshots": true
  },
  "security_questions": {
    "doğduğunuz kasabanın/şehrin adı nedir?": "Ankara",
    "eşinizle nerede tanıştınız?": "otobus"
  },
  "proxy": {
    "enabled": true,
    "server": "geo.iproyal.com:12321",
    "username": "your_proxy_username",
    "password": "your_proxy_password"
  }
}
```

## Usage

### Run Complete Flow
```bash
python run_bot.py --mode full
```

### Run Login Only
```bash
python run_bot.py --mode login
```

### Test Navigation
```bash
python run_bot.py --mode test
```

### Direct Bot Usage
```bash
python ustraveldocs_bot.py
```

## Bot Flow

1. **Initialize Browser**: Sets up Playwright with anti-bot measures
2. **Navigate to Visa Entry**: Goes to ustraveldocs.com visa section
3. **Access Login**: Finds and clicks visa entry/login buttons
4. **Perform Login**: Fills credentials and handles captcha
5. **Security Questions**: Intelligently answers Turkish security questions
6. **Appointment Scheduling**: Navigates to appointment rescheduling interface

## Anti-Bot Features

- Custom user agent and browser fingerprinting
- Proxy support with authentication
- Human-like interaction patterns (delays, mouse movements)
- Popup and overlay handling
- Advanced captcha solving integration
- Session persistence

## Security Questions

The bot includes intelligent matching for Turkish security questions:

- Doğduğunuz kasabanın/şehrin adı nedir? → Ankara
- Eşinizle nerede tanıştınız? → otobus
- Büyüdüğünüz yolun/sokağın adı nedir? → Sokak
- İlk evcil hayvanınızın adı nedir? → Karabaş
- İlkokul öğretmeninizin soyadı nedir? → Yılmaz
- Annenizin kızlık soyadı nedir? → Demir
- En sevdiğiniz renk nedir? → Mavi

## Troubleshooting

### Common Issues

1. **Captcha Solving Fails**
   - Verify 2captcha API key is correct
   - Check 2captcha account balance
   - Try running with `headless: false` to manually solve

2. **Proxy Connection Issues**
   - Verify proxy credentials in config.json
   - Test proxy connection manually
   - Try disabling proxy temporarily

3. **Login Fails**
   - Verify username/password in config.json
   - Check if account is locked
   - Try manual login first

4. **Security Questions Fail**
   - Verify answers match exactly (case-sensitive)
   - Check Turkish character encoding
   - Update security_questions in config.json

### Debug Mode

Run with screenshots enabled to debug issues:
```json
{
  "config": {
    "save_screenshots": true,
    "headless": false
  }
}
```

Screenshots will be saved in the `screenshots/` directory.

## Dependencies

- Python 3.8+
- playwright>=1.40.0
- httpx>=0.25.0
- asyncio-mqtt>=0.13.0

## License

This project is for educational purposes only. Use responsibly and in accordance with the target website's terms of service.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub or contact the maintainer.

---

**Note**: This bot is designed to work with ustraveldocs.com as of 2025. Website changes may require updates to the bot logic.
