#!/usr/bin/env python3


from cat_royale.main import main_func


if __name__ == "__main__":

    import unittest
    import argparse
    parser = argparse.ArgumentParser(description="CatRoyale")
    parser.add_argument("--test", action="store_true", help="Start testing")
    args = parser.parse_args()
    if args.test:
        import pygame

        from cat_royale.classes.message_service import MessageService
        from cat_royale.classes.functions import scale_image
        from cat_royale.classes.config import Config
        from cat_royale.classes.health_bars import HealthBar
        from cat_royale.classes.map_reader import read_map_image
        from cat_royale.classes.functions import get_item_sprite_image
        from cat_royale.main import load_config
        from cat_royale.classes.event_stack import EventStack, Event, WindowStack
        from cat_royale.classes.box import Box
        from cat_royale.classes.inventory import Inventory
        from cat_royale.classes.item import Item, ITEM
        pygame.init()
        load_config()

        class TestCatRoyale(unittest.TestCase):

            def setUp(self) -> None:
                self.screen = pygame.display.set_mode(
                    (1, 1))
                return super().setUp()

            def testImageScale(self):
                img = pygame.image.load(
                    Config.images["cat"]).convert_alpha()

                self.assertEqual(scale_image(get_item_sprite_image(
                    img, 1, 1)[0], 2).get_size(), (64, 64), msg="Image scale is not correct")

            def testReadMap(self):
                self.assertEqual(read_map_image(
                    Config.images["level00"])[0], (100, 100))

            def testMessageService(self):
                MessageService.add({"text": "test", "severity": "info"})
                self.assertEqual(MessageService.next(), {
                                 "text": "test", "severity": "info"})
                self.assertEqual(MessageService.next(), None)

            def testHealthBar(self):
                health_bar = HealthBar(0)
                health_bar.hp = 101
                self.assertEqual(health_bar.hp, 100)
                health_bar.hp = -1
                self.assertEqual(health_bar.hp, 0)
                health_bar.hp = 10
                self.assertEqual(health_bar.hp, 10)

            def testEventStack(self):
                def x(): return print("test_successful")
                event = Event("test", x)
                EventStack.push(event)
                self.assertIsNotNone(EventStack.find_event(event))
                EventStack.call_and_pop('test')
                self.assertIsNone(EventStack.find_event(event))

            def testBox(self):
                def x(): return print("test_successful")

                box = Box((40, 40), True, x)
                box.opened = True
                self.assertIn(box, WindowStack.stack)
                box.opened = False
                self.assertNotIn(box, WindowStack.stack)

            def testInventory(self):
                inv = Inventory()
                img = pygame.Surface((64, 64))
                items = [Item(img, ITEM['WOOD'], 1)
                         for x in range(10)]
                for item in items:
                    inv.add_item_to_stack(item)
                self.assertTrue(inv.isFull)
                removed = inv.remove_item_from_slot(0)
                self.assertEqual(removed, items[0])
                inv.subtract_item(ITEM["WOOD"], 1)
                empty_slots = [None
                               for x in inv.slots if inv.slots[x] is None]
                self.assertEqual(len(empty_slots), 2)

        unittest.main(argv=[''], exit=False, defaultTest='TestCatRoyale')

    else:
        print("Starting CatRoyale...")
        main_func()
