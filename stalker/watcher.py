import time
import os
import codex_client
import urllib3
from typing import List, Callable

from . import models, utils

AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE = os.environ.get("AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE", 20)
MAX_FAILED_POLLS = os.environ.get("MAX_FAILED_POLLS", 20)


def watch_loop(node_url: str, notifiers: List[Callable[[str], None]], poll_seconds=5):
    configuration = codex_client.Configuration(
        host=node_url + ('/' if node_url[-1] != '/' else '') + 'api/codex/v1'
    )

    with codex_client.ApiClient(configuration) as api_client:
        marketplace = codex_client.MarketplaceApi(api_client)
        failed_polls = 0

        print("Starting to monitor Codex node")
        while True:
            try:
                # Purchases monitoring
                _monitor_purchases(marketplace, notifiers)

                # Availabilities monitoring
                _monitor_availabilities(marketplace, notifiers)

                # Slots monitoring
                _monitor_slots(marketplace, notifiers)
            except urllib3.exceptions.MaxRetryError:
                print("Not able to connect to Codex node!")
                failed_polls += 1

                if failed_polls > MAX_FAILED_POLLS:
                    raise ConnectionError("Can not connect to Codex node!")

            time.sleep(poll_seconds)


def _monitor_slots(marketplace: codex_client.MarketplaceApi, notifiers: List[Callable[[str], None]]):
    fetched_slots = [(slot.id, marketplace.get_active_slot_by_id(slot.id)) for slot in marketplace.get_active_slots()]

    for (fetched_slot_id, fetched_slot) in fetched_slots:

        try:
            current_slot = models.Slot.objects.get(pk=fetched_slot_id)

            if current_slot.state != fetched_slot.state:
                _notify(notifiers,
                        f"Slot {utils.format_id(current_slot.id)} moved to state {fetched_slot.state}.")

                current_slot.state = fetched_slot.state
                current_slot.save()

        except models.Slot.DoesNotExist:
            models.Slot(id=fetched_slot_id, state=fetched_slot.state).save()
            _notify(notifiers,
                    f"New slot {utils.format_id(fetched_slot_id)} with size of "
                    f"{utils.format_size(fetched_slot.request.ask.slot_size)} and reward {utils.get_reward(fetched_slot.request.ask)} "
                    f"which will be hosted until {utils.format_duration(fetched_slot.request.ask.duration)}.")
            continue

    fetched_slot_ids = set(slot[0] for slot in fetched_slots)
    current_slot_ids = set(slot.id for slot in models.Slot.objects.all())

    # Remove slots from models.Slot that are not in fetched_slots
    for slot_id in current_slot_ids.difference(fetched_slot_ids):
        try:
            slot_to_remove = models.Slot.objects.get(pk=slot_id)
            _notify(notifiers,
                    f"Removing slot {utils.format_id(slot_to_remove.id)} from tracking.")
            slot_to_remove.delete()
        except models.Slot.DoesNotExist:
            pass


def _monitor_availabilities(marketplace: codex_client.MarketplaceApi, notifiers: List[Callable[[str], None]]):
    fetched_availabilities = marketplace.get_availabilities()

    for fetched_availability in fetched_availabilities:
        try:
            current_availability = models.Availability.objects.get(pk=fetched_availability.id)
            fetched_availability_free_size = int(fetched_availability.free_size)

            if current_availability.freeSize != fetched_availability_free_size:
                # freeSize decreased from the last check, and it has fallen below the threshold
                if current_availability.freeSize < fetched_availability_free_size < (
                        int(fetched_availability.total_size) / 100 * AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE):
                    _notify(notifiers,
                            f"Availability's {utils.format_id(fetched_availability.id)} free size has fallen bellow {utils.format_size(int(fetched_availability.total_size) / 100 * AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE)}")

                current_availability.freeSize = fetched_availability_free_size
                current_availability.save()
        except ValueError:
            print("FreeSize was not possible to convert to int!")
        except models.Availability.DoesNotExist:
            models.Availability(id=fetched_availability.id, freeSize=int(fetched_availability.free_size)).save()
            _notify(notifiers,
                    f"New availability {utils.format_id(fetched_availability.id)} with size "
                    f"{utils.format_size(int(fetched_availability.total_size))}.")
            continue

    fetched_availability_ids = set(availability.id for availability in fetched_availabilities)
    current_availability_ids = set(availability.id for availability in models.Availability.objects.all())

    # Remove availabilities from models.Availability that are not in fetched_availabilities
    for availability_id in current_availability_ids.difference(fetched_availability_ids):
        try:
            availability_to_remove = models.Availability.objects.get(pk=availability_id)
            _notify(notifiers,
                    f"Removing availability {utils.format_id(availability_to_remove.id)} from tracking.")
            availability_to_remove.delete()
        except models.Availability.DoesNotExist:
            pass


def _monitor_purchases(marketplace: codex_client.MarketplaceApi, notifiers: List[Callable[[str], None]]):
    fetched_purchases = [(purchase_id, marketplace.get_purchase(purchase_id)) for purchase_id in
                         marketplace.get_purchases()]

    for [fetched_purchase_id, fetched_purchase] in fetched_purchases:
        try:
            current_purchase = models.Purchase.objects.get(pk=fetched_purchase_id)

            if current_purchase.state != fetched_purchase.state:
                _notify(notifiers,
                        f"Purchase {utils.format_id(current_purchase.id)} moved to state {fetched_purchase.state}.")
                current_purchase.state = fetched_purchase.state
                current_purchase.save()
        except:
            models.Purchase(id=fetched_purchase_id, state=fetched_purchase.state).save()
            # TODO: More details on the new purchase? CID? Price? Duration?
            _notify(notifiers,
                    f"New purchase {utils.format_id(fetched_purchase_id)} in state {fetched_purchase.state}.")
            continue

    fetched_purchase_ids = set(purchase[0] for purchase in fetched_purchases)
    current_purchase_ids = set(purchase.id for purchase in models.Purchase.objects.all())

    # Remove purchases from models.Purchase that are not in fetched_purchases
    for purchase_id in current_purchase_ids.difference(fetched_purchase_ids):
        try:
            purchase_to_remove = models.Purchase.objects.get(pk=purchase_id)
            _notify(notifiers,
                    f"Removing purchase {utils.format_id(purchase_to_remove.id[:5])} from tracking.")
            purchase_to_remove.delete()
        except models.Purchase.DoesNotExist:
            pass


def _notify(notifiers: List[Callable[[str], None]], msg: str):
    for notifier in notifiers:
        notifier(msg)
