#!/usr/bin/env python3
"""
USTravelDocs Bot Runner

Simple entry point script for running the USTravelDocs bot with different modes.
"""

import asyncio
import argparse
import sys
from ustraveldocs_bot import USTravelDocsBot

async def run_login_only():
    """Run only the login flow"""
    bot = USTravelDocsBot()
    try:
        await bot.initialize_browser()
        await bot.navigate_to_visa_entry()
        await bot.navigate_to_login()
        await bot.perform_login()
        print("✅ Login completed successfully!")
        print("📱 Browser will remain open...")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ Login failed: {e}")
    finally:
        await bot.cleanup()

async def run_full_flow():
    """Run the complete bot flow"""
    bot = USTravelDocsBot()
    try:
        success = await bot.run_complete_flow()
        if success:
            print("✅ Full flow completed successfully!")
            print("📱 Browser will remain open...")
            await asyncio.Event().wait()
        else:
            print("❌ Full flow failed!")
    except Exception as e:
        print(f"❌ Full flow error: {e}")
    finally:
        await bot.cleanup()

async def run_test_navigation():
    """Test only navigation to visa entry"""
    bot = USTravelDocsBot()
    try:
        await bot.initialize_browser()
        await bot.navigate_to_visa_entry()
        print("✅ Navigation test completed!")
        print("📱 Browser will remain open for 30 seconds...")
        await asyncio.sleep(30)
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
    finally:
        await bot.cleanup()

def main():
    parser = argparse.ArgumentParser(description='USTravelDocs Bot Runner')
    parser.add_argument('--mode', choices=['full', 'login', 'test'], default='full',
                       help='Bot execution mode (default: full)')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path (default: config.json)')
    
    args = parser.parse_args()
    
    print(f"\n🤖 USTravelDocs Bot Runner")
    print(f"Mode: {args.mode}")
    print(f"Config: {args.config}")
    print("=" * 50)
    
    try:
        if args.mode == 'full':
            asyncio.run(run_full_flow())
        elif args.mode == 'login':
            asyncio.run(run_login_only())
        elif args.mode == 'test':
            asyncio.run(run_test_navigation())
    except KeyboardInterrupt:
        print("\n⚠️ Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
