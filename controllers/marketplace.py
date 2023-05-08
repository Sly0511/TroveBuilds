import asyncio
from datetime import datetime

import requests
from flet import (
    TextField,
    Card,
    Column,
    ResponsiveRow,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    Dropdown,
    dropdown,
    Text,
    Row,
    Image,
    Icon,
    ElevatedButton,
    Container,
    MainAxisAlignment,
    ProgressRing,
    IconButton,
    DragTarget,
    Draggable,
    border
)
from flet_core.icons import REPORT, VERIFIED, ARROW_FORWARD_IOS, ARROW_BACK_IOS

from models.objects import Controller
from models.objects.marketplace import Item
from models.objects.marketplace import Listing, ListingStatus
from models.objects.user import User
from utils import tasks
from utils.controls import ScrollingFrame
from utils.functions import long_throttle, throttle, chunks

MARKET_MAX_SALE = 9999 * 9999 * 16


class MarketplaceSettings:
    selected_item = None
    create_category = None
    create_word = None
    create_amount = None
    create_price = None
    search_word = None
    listing_statuses = [ListingStatus.pending, ListingStatus.listed]
    listings_max_pages = 0
    listings_page = 0
    listings_per_page = 10
    listings_max_listings = 0
    ylistings_max_pages = 0
    ylistings_page = 0
    ylistings_per_page = 4
    ylistings_max_listings = 0


listing_colors = {
    ListingStatus.listed: "#2d8add",
    ListingStatus.pending: "#f1c232",
    ListingStatus.sold: "#4d982c",
    ListingStatus.cancelled: "#e71d1d",
    ListingStatus.expired: "#a23ef3"
}


class MarketplaceController(Controller):
    def setup_controls(self):
        if not getattr(self.page.constants, "trove_items"):
            self.main = Column(
                controls=[ProgressRing(), Text("Loading items")],
                width=self.page.width,
                height=self.page.height,
                alignment="center",
                horizontal_alignment="center",
            )
            self.get_items_list.start()
            return
        if not hasattr(self, "market"):
            self.items = self.page.constants.trove_items
            self.categories = sorted(
                list(
                    set([i.category for i in self.items if i.category and i.marketable])
                )
            )
            self.market = MarketplaceSettings()
            self.main = ResponsiveRow(
                disabled=True  # not bool(self.page.constants.discord_user)
            )
            self.listings = DataTable(
                columns=[
                    DataColumn(Text("ID")),
                    DataColumn(Text("Item")),
                    DataColumn(Text("Price")),
                    DataColumn(Text("Tank Price")),
                    DataColumn(Text("Amount")),
                    DataColumn(Text("Price Each")),
                    DataColumn(Text("")),
                ],
                col=12,
            )
            self.your_listings = ResponsiveRow(alignment="center")
        self.main.controls.clear()
        self.main.controls.extend(
            [
                Card(
                    ResponsiveRow(
                        controls=[
                            Column(
                                controls=[
                                    Text("Create listing", size=22),
                                    Dropdown(
                                        options=[
                                            dropdown.Option(key="none", text="<clear>")
                                        ]
                                        + [
                                            dropdown.Option(key=c, text=c.capitalize())
                                            for c in self.categories
                                        ],
                                        value=self.market.create_category,
                                        on_change=self.change_category,
                                    ),
                                    TextField(
                                        label="Item",
                                        value=self.market.create_word,
                                        on_change=self.change_create_word,
                                    ),
                                    TextField(
                                        label="Amount",
                                        value=(
                                            f"{self.market.create_amount} ".replace(
                                                ".0 ", ""
                                            ).strip()
                                            if self.market.create_amount
                                            else self.market.create_amount
                                        ),
                                        on_change=self.set_create_amount,
                                    ),
                                    TextField(
                                        label="Price each",
                                        value=(
                                            f"{self.market.create_price} ".replace(
                                                ".0 ", ""
                                            ).strip()
                                            if self.market.create_price
                                            else self.market.create_price
                                        ),
                                        on_change=self.set_create_price,
                                    ),
                                    Row(
                                        controls=[
                                            ElevatedButton(
                                                "Create listing",
                                                data=self.market.selected_item,
                                                disabled=(
                                                    not bool(self.market.selected_item)
                                                    or not bool(
                                                        self.market.create_price
                                                    )
                                                    or not bool(
                                                        self.market.create_amount
                                                    )
                                                )
                                                or (
                                                    self.market.create_amount
                                                    and self.market.create_price
                                                    and self.market.create_price
                                                    * self.market.create_amount
                                                    > MARKET_MAX_SALE
                                                ),
                                                on_click=self.create_listing,
                                            ),
                                            *(
                                                [
                                                    Image(
                                                        src="assets/images/resources/item_crafting_spark.png",
                                                        width=35,
                                                    ),
                                                    Text(
                                                        f"{int(self.market.create_price * self.market.create_amount):,}"
                                                    ),
                                                ]
                                                if self.market.create_amount
                                                and self.market.create_price
                                                else [Text("")]
                                            ),
                                            *(
                                                [
                                                    Text("or"),
                                                    Image(
                                                        src="assets/images/resources/item_crafting_fluxcannister.png",
                                                        width=35,
                                                    ),
                                                    Text(f"{int(price // 9999):,}"),
                                                    Image(
                                                        src="assets/images/resources/item_crafting_spark.png",
                                                        width=35,
                                                    ),
                                                    Text(f"{int(price % 9999):,}"),
                                                ]
                                                if self.market.create_amount
                                                and self.market.create_price
                                                and (
                                                    price := int(
                                                        self.market.create_price
                                                        * self.market.create_amount
                                                    )
                                                )
                                                >= 150_000
                                                else []
                                            ),
                                            (
                                                Text(
                                                    f"Max Price: {MARKET_MAX_SALE:,}",
                                                    color="red",
                                                )
                                                if self.market.create_amount
                                                and self.market.create_price
                                                and self.market.create_price
                                                * self.market.create_amount
                                                > MARKET_MAX_SALE
                                                else Text("")
                                            ),
                                        ]
                                    ),
                                ],
                                horizontal_alignment="center",
                                col={"xxl": 5},
                            ),
                            Column(
                                controls=[
                                    DataTable(
                                        columns=[
                                            DataColumn(Text("")),
                                            DataColumn(Text("")),
                                            DataColumn(Text("")),
                                            DataColumn(Text("")),
                                        ],
                                        rows=[
                                            DataRow(
                                                cells=[
                                                    DataCell(
                                                        Image(
                                                            src_base64=i.icon_base64,
                                                            width=35,
                                                        ),
                                                        data=i,
                                                        on_tap=self.set_create_word,
                                                    ),
                                                    DataCell(
                                                        Text(i.name),
                                                        data=i,
                                                        on_tap=self.set_create_word,
                                                    ),
                                                    DataCell(
                                                        Icon(
                                                            REPORT,
                                                            size=25,
                                                            tooltip="Report invalid item.",
                                                        ),
                                                        data=i,
                                                        on_tap=self.report_item,
                                                        disabled=i.reported
                                                        or i.verified,
                                                    ),
                                                    DataCell(
                                                        Icon(
                                                            VERIFIED,
                                                            size=25,
                                                            tooltip="Verify item.",
                                                        ),
                                                        data=i,
                                                        on_tap=self.verify_item,
                                                        disabled=i.verified,
                                                    ),
                                                ]
                                            )
                                            for i in list(
                                                filter(self.filter_items, self.items)
                                            )[:7]
                                            if self.market.create_word
                                        ],
                                        heading_row_height=0,
                                        visible=bool(self.market.create_word),
                                    ),
                                ],
                                horizontal_alignment="center",
                                scroll="auto",
                                col={"xxl": 7},
                            ),
                        ]
                    ),
                    margin=5,
                    col={"xxl": 5},
                ),
                Card(
                    Column(
                        controls=[Text("Your Listings", size=22), self.your_listings],
                        horizontal_alignment="center",
                    ),
                    margin=5,
                    col={"xxl": 7},
                ),
            ]
        )
        self.main.controls.extend(
            [
                TextField(
                    label="Search item",
                    value=self.market.search_word,
                    on_submit=self.set_search_word,
                    col={"xxl": 4},
                )
            ]
        )
        asyncio.create_task(self.update_listings())
        asyncio.create_task(self.update_your_listings())
        self.main.controls.append(ScrollingFrame(self.listings))

    def setup_events(self):
        ...

    async def update_listings(self):
        self.listings.rows.clear()
        if self.market.search_word:
            async for listing in Listing.find_many({}, limit=10, fetch_links=True):
                ...
        while True:
            await asyncio.sleep(1)
            try:
                await self.listings.update_async()
                break
            except Exception:
                ...

    async def next_your_listings(self, event):
        self.market.ylistings_page += 1
        if self.market.ylistings_page > self.market.ylistings_max_pages - 1:
            self.market.ylistings_page = 0
        await self.update_your_listings()

    async def previous_your_listings(self, event):
        self.market.ylistings_page -= 1
        if self.market.ylistings_page < 0:
            self.market.ylistings_page = self.market.ylistings_max_pages - 1
        await self.update_your_listings()

    @throttle
    async def update_your_listings(self, event=None):
        self.your_listings.controls.clear()
        self.your_listings.controls.append(
            Row(controls=[ProgressRing(), Text("Loading listings...")])
        )
        await self.your_listings.update_async()
        self.your_listings.controls.clear()
        listings = list(
            filter(
                lambda x: x.status in self.market.listing_statuses,
                await Listing.find_many({}, fetch_links=True).to_list(
                    length=999999
                )
            )
        )
        listings.sort(key=lambda x: (self.market.listing_statuses.index(x.status), x.created_at))
        self.market.ylistings_max_listings = len(listings)
        listing_chunks = chunks(listings, self.market.ylistings_per_page)
        self.market.ylistings_max_pages = len(listing_chunks)
        if self.market.ylistings_page > self.market.ylistings_max_pages:
            self.market.ylistings_page = self.market.ylistings_max_pages
        if self.market.ylistings_page < 0:
            self.market.ylistings_page = 0
        if not self.market.ylistings_max_listings:
            self.your_listings.controls.append(
                Text("You haven't listed any items.", size=20)
            )
        else:
            for listing in listing_chunks[self.market.ylistings_page]:
                # Prevent listing others' listings
                if listing.seller.discord_id != int(self.page.constants.discord_user.id):
                    continue
                actions = []
                if listing.status in [ListingStatus.listed, ListingStatus.pending]:
                    actions.append(
                        ElevatedButton(
                            "Cancel",
                            color="yellow",
                            data=listing,
                            on_click=self.cancel_listing,
                            height=25,
                        )
                    )
                actions.append(
                    ElevatedButton(
                        "Relist",
                        data=listing,
                        on_click=self.relist_listing,
                        height=25,
                    )
                )
                if listing.status in [ListingStatus.pending]:
                    actions.append(
                        ElevatedButton(
                            "Approve",
                            color="green",
                            data=listing,
                            on_click=self.cancel_listing,
                            height=25,
                        )
                    )
                    actions.append(
                        ElevatedButton(
                            "Deny",
                            color="red",
                            data=listing,
                            on_click=self.cancel_listing,
                            height=25,
                        )
                    )

                # Filter listings with bad status
                self.your_listings.controls.append(
                    Card(
                        content=Row(
                            controls=[
                                Image(src_base64=listing.item.icon_base64, width=125),
                                Column(
                                    controls=[
                                        Container(
                                            Row(
                                                controls=[
                                                    Text(f"[{listing.status.value}]", color=listing_colors[listing.status]),
                                                    Text(listing.item.name, color="cyan"),
                                                ]
                                            ),
                                            data=listing.item.trovesaurus_url,
                                            on_click=self.go_to_url,
                                            tooltip="Click me for more information",
                                        ),
                                        Row(
                                            controls=[
                                                Card(
                                                    *(
                                                        [
                                                            Row(
                                                                controls=[
                                                                    Image(
                                                                        src="assets/images/resources/item_crafting_spark.png",
                                                                        width=20,
                                                                    ),
                                                                    Text(
                                                                        f"{listing.price:,}",
                                                                        size=12,
                                                                    ),
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                    surface_tint_color="red",
                                                ),
                                                *[
                                                    Text("or", size=12)
                                                    if listing.price >= 150_000
                                                    else Text()
                                                ],
                                                Card(
                                                    *(
                                                        [
                                                            Row(
                                                                controls=[
                                                                    Image(
                                                                        src="assets/images/resources/item_crafting_fluxcannister.png",
                                                                        width=20,
                                                                    ),
                                                                    Text(
                                                                        f"{int(listing.better_price[0]):,}",
                                                                        size=12,
                                                                    ),
                                                                    Image(
                                                                        src="assets/images/resources/item_crafting_spark.png",
                                                                        width=20,
                                                                    ),
                                                                    Text(
                                                                        f"{int(listing.better_price[1]):,}",
                                                                        size=12,
                                                                    ),
                                                                ]
                                                            )
                                                        ]
                                                        if listing.price >= 150_000
                                                        else []
                                                    ),
                                                    surface_tint_color="red",
                                                ),
                                            ]
                                        ),
                                        Row(
                                            controls=[
                                                Card(
                                                    content=Row(
                                                        controls=[
                                                            Text("Quantity:", size=12),
                                                            Text(
                                                                f"{listing.amount:,}",
                                                                size=12,
                                                            ),
                                                        ]
                                                    ),
                                                    surface_tint_color="red",
                                                ),
                                                Card(
                                                    content=Row(
                                                        controls=[
                                                            Text("Price Each:", size=12),
                                                            Image(
                                                                src="assets/images/resources/item_crafting_spark.png",
                                                                width=20,
                                                            ),
                                                            Text(
                                                                f"{listing.price_per:,g}",
                                                                size=12,
                                                            ),
                                                        ]
                                                    ),
                                                    surface_tint_color="red",
                                                ),
                                            ]
                                        ),
                                        Row(
                                            controls=actions,
                                            alignment=MainAxisAlignment.END,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                            ]
                        ),
                        surface_tint_color=listing_colors[listing.status],
                        col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 6, "xxl": 6},
                        margin=10,
                    )
                )
        self.your_listings.controls.append(
            ResponsiveRow(
                controls=[
                    Card(
                        DragTarget(
                            content=ResponsiveRow(
                                controls=[
                                    Card(
                                        Draggable(
                                            data=status,
                                            content=Text(
                                                status.value,
                                                text_align="center",
                                            ),
                                            content_feedback=Card(
                                                content=Text(
                                                    status.value,
                                                    text_align="center"
                                                ),
                                                width=80,
                                                color=listing_colors[status]
                                            ),
                                            group="unused"
                                        ),
                                        color=listing_colors[status],
                                        col=12 / len(ListingStatus)
                                    )
                                    for status in ListingStatus
                                    if status in self.market.listing_statuses
                                ] + [
                                    Card(col=12 / len(ListingStatus))
                                    for _ in range(len(ListingStatus) - len(self.market.listing_statuses))
                                ]
                            ),
                            group="used",
                            on_accept=self.drag_ylisting_used_status,
                            on_will_accept=self.drag_will_accept,
                            on_leave=self.drag_leave
                        ),
                        surface_tint_color="blue",
                        col=6
                    ),
                    Card(
                        DragTarget(
                            content=ResponsiveRow(
                                controls=[
                                    Card(
                                        Draggable(
                                            data=status,
                                            content=Text(
                                                status.value,
                                                text_align="center"
                                            ),
                                            content_feedback=Card(
                                                content=Text(
                                                    status.value,
                                                    text_align="center"
                                                ),
                                                width=80,
                                                color=listing_colors[status]
                                            ),
                                            group="used"
                                        ),
                                        color=listing_colors[status],
                                        col=12 / len(ListingStatus)
                                    )
                                    for status in ListingStatus
                                    if status not in self.market.listing_statuses
                                ] + [
                                    Card(col=12 / len(ListingStatus))
                                    for _ in range(len(self.market.listing_statuses))
                                ]
                            ),
                            group="unused",
                            on_accept=self.drag_ylisting_unused_status,
                            on_will_accept=self.drag_will_accept,
                            on_leave=self.drag_leave
                        ),
                        surface_tint_color="blue",
                        col=6
                    ),
                ]
            )
        )
        self.your_listings.controls.append(
            ResponsiveRow(
                controls=[
                    Text(
                        col={
                            "xs": 0,
                            "sm": 1.5,
                            "md": 1.5,
                            "lg": 1.5,
                            "xl": 2,
                            "xxl": 3.5
                        }
                    ),
                    IconButton(
                        ARROW_BACK_IOS,
                        disabled=self.market.ylistings_max_pages == 1,
                        on_click=self.previous_your_listings,
                        col={"xs": 3, "sm": 3, "md": 3, "lg": 3, "xl": 3, "xxl": 2},
                    ),
                    Text(
                        f"Page {self.market.ylistings_page+1} of {self.market.ylistings_max_pages}",
                        text_align="center",
                        col={"xs": 5, "sm": 3, "md": 3, "lg": 3, "xl": 3, "xxl": 1},
                    ),
                    IconButton(
                        ARROW_FORWARD_IOS,
                        disabled=self.market.ylistings_max_pages == 1,
                        on_click=self.next_your_listings,
                        col={"xs": 3, "sm": 3, "md": 3, "lg": 3, "xl": 3, "xxl": 2},
                    ),
                    Text(
                        col={
                            "xs": 0,
                            "sm": 1.5,
                            "md": 1.5,
                            "lg": 1.5,
                            "xl": 2,
                            "xxl": 3.5,
                        }
                    ),
                ]
            )
        )
        while True:
            await asyncio.sleep(1)
            try:
                await self.your_listings.update_async()
                break
            except Exception:
                ...

    def filter_items(self, item):
        if self.market.create_category and item.category != self.market.create_category:
            return False
        if (
            self.market.create_word
            and self.market.create_word.lower() not in item.name.lower()
        ):
            return False
        return item.marketable

    @long_throttle
    async def change_create_word(self, event):
        self.market.selected_item = None
        self.market.create_word = event.control.value
        self.setup_controls()
        await self.page.update_async()

    async def set_create_word(self, event):
        self.market.selected_item = event.control.data
        self.market.create_word = event.control.data.name
        self.setup_controls()
        await self.page.update_async()

    async def change_category(self, event):
        if event.control.value == "none":
            self.market.create_category = None
        else:
            self.market.create_category = event.control.value
        self.setup_controls()
        await self.page.update_async()

    async def report_item(self, event):
        if event.control.data.reported:
            self.page.snack_bar.content.value = "Item already reported"
            self.page.snack_bar.open = True
            return await self.page.update_async()
        event.control.data.reported = True
        message = {
            "username": "Item Report Logs",
            "content": "Item reported as non tradeable.",
            "embeds": [
                {
                    "title": event.control.data.name,
                    "thumbnail": {"url": event.control.data.icon_url},
                    "color": 0x990000,
                    "fields": [
                        {
                            "name": "Item ID",
                            "value": event.control.data.identifier,
                            "inline": False,
                        },
                        {
                            "name": "Reported by",
                            "value": "#".join(
                                [
                                    self.page.discord_user.username,
                                    self.page.discord_user.discriminator,
                                ]
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Reporter ID",
                            "value": self.page.constants.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Reported"},
                }
            ],
        }
        resp = requests.post(self.page.constants.market_log_webhook, json=message)
        if resp.status_code == 204:
            await event.control.data.save()
            self.page.snack_bar.content.value = "Item reported for removal"
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar.content.value = "Failed to report item, try again"
            self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    async def verify_item(self, event):
        if event.control.data.reported:
            self.page.snack_bar.content.value = "Item already reported"
            self.page.snack_bar.open = True
            return await self.page.update_async()
        event.control.data.reported = True
        message = {
            "username": "Item Verification Requests",
            "content": "Requested verification for item that it's tradeable.",
            "embeds": [
                {
                    "title": event.control.data.name,
                    "thumbnail": {"url": event.control.data.icon_url},
                    "color": 0x009900,
                    "fields": [
                        {
                            "name": "Item ID",
                            "value": event.control.data.identifier,
                            "inline": False,
                        },
                        {
                            "name": "Reported by",
                            "value": "#".join(
                                [
                                    self.page.constants.discord_user.username,
                                    self.page.constants.discord_user.discriminator,
                                ]
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Reporter ID",
                            "value": self.page.constants.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Reported"},
                }
            ],
        }
        resp = requests.post(self.page.constants.market_log_webhook, json=message)
        if resp.status_code == 204:
            await event.control.data.save()
            self.page.snack_bar.content.value = "Item reported for verification"
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar.content.value = "Failed to report item, try again"
            self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    @throttle
    async def set_create_amount(self, event):
        event.control.border_color = None
        try:
            amount = int(event.control.value)
            self.market.create_amount = amount
        except ValueError:
            event.control.border_color = "red"
        self.setup_controls()
        await self.page.update_async()

    @long_throttle
    async def set_create_price(self, event):
        event.control.border_color = None
        try:
            amount = float(event.control.value.replace(",", "."))
            self.market.create_price = amount
        except ValueError:
            event.control.border_color = "red"
        self.setup_controls()
        await self.page.update_async()

    async def set_search_word(self, event):
        self.market.search_word = event.control.value
        self.setup_controls()
        await self.page.update_async()

    async def create_listing(self, event):
        event.control.disabled = True
        await event.control.update_async()
        message = {
            "username": "Listing creation",
            "content": "A listing was created.",
            "embeds": [
                {
                    "title": event.control.data.name,
                    "thumbnail": {"url": event.control.data.icon_url},
                    "color": 0x000099,
                    "fields": [
                        {
                            "name": "Item ID",
                            "value": event.control.data.identifier,
                            "inline": False,
                        },
                        {
                            "name": "Created by",
                            "value": "#".join(
                                [
                                    self.page.constants.discord_user.username,
                                    self.page.constants.discord_user.discriminator,
                                ]
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Creator ID",
                            "value": self.page.constants.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Created"},
                }
            ],
        }
        resp = requests.post(self.page.constants.market_log_webhook, json=message)
        if resp.status_code == 204:
            user = await User.find_one(
                User.discord_id == int(self.page.constants.discord_user.id)
            )
            listing = Listing(
                item=self.market.selected_item,
                seller=user,
                price=int(self.market.create_amount * self.market.create_price),
                amount=self.market.create_amount,
            )
            await listing.save()
            self.market.create_word = None
            self.market.create_price = None
            self.market.create_amount = None
            self.page.snack_bar.content.value = "Item listed"
            self.page.snack_bar.open = True
            self.setup_controls()
            await self.update_listings()
            await self.page.update_async()

    async def buy_listing(self, event):
        event.control.disabled = True
        await event.control.update_async()

    async def copy_to_clipboard(self, event):
        if value := event.control.content.value:
            await self.page.set_clipboard_async(str(value))
            self.page.snack_bar.content.value = "Copied to clipboard"
            self.page.snack_bar.open = True
        await self.page.update_async()

    async def go_to_url(self, event):
        await self.page.launch_url_async(event.control.data)

    @tasks.loop(seconds=1)
    async def get_items_list(self):
        data = requests.get("https://trovesaurus.com/items.json").json()
        for raw_item in data:
            item = await Item.find_one(Item.identifier == raw_item["identifier"])
            if item is None:
                item = await Item(**raw_item).save()
            else:
                item.name = raw_item["name"]
                item.type = raw_item["type"]
                item.description = raw_item["description"]
                item.icon = raw_item["icon"]
                item.notrade = raw_item["notrade"]
                item.noobtain = raw_item["noobtain"]
            self.page.constants.trove_items.append(item)
        await self.page.restart()
        self.get_items_list.cancel()

    async def relist_listing(self, event):
        self.market.create_amount = event.control.data.amount
        self.market.create_price = event.control.data.price_per
        self.market.selected_item = event.control.data.item
        self.market.create_word = event.control.data.item.name
        self.setup_controls()
        await self.page.update_async()

    async def cancel_listing(self, event):
        event.control.data.status = ListingStatus.cancelled
        await event.control.data.save()
        self.setup_controls()
        await self.update_your_listings()

    async def drag_ylisting_used_status(self, event):
        src = self.page.get_control(event.src_id)
        self.market.listing_statuses.append(src.data)
        await self.update_your_listings()

    async def drag_ylisting_unused_status(self, event):
        src = self.page.get_control(event.src_id)
        self.market.listing_statuses.remove(src.data)
        await self.update_your_listings()

    async def drag_will_accept(self, event):
        event.control.border = border.all(
            2, None if event.data == "true" else "red"
        )
        await event.control.update_async()

    async def drag_leave(self, event):
        event.control.content.border = None
        await event.control.update_async()
