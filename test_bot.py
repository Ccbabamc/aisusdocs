#!/usr/bin/env python3
"""
Test script to verify bot functionality
"""

import sys
import json
import asyncio
from ustraveldocs_bot import USTravelDocsBot

async def test_bot_initialization():
    """Test bot initialization and configuration loading"""
    try:
        bot = USTravelDocsBot()
        print("✅ Bot initialization successful")
        print(f"✅ Configuration loaded: {bool(bot.config)}")
        
        await bot.initialize_browser()
        print("✅ Browser initialization successful")
        
        await bot.navigate_to_visa_entry()
        print("✅ Navigation to visa entry successful")
        
        await bot.cleanup()
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot_initialization())
    sys.exit(0 if success else 1)
