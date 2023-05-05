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
    VerticalDivider,
    MainAxisAlignment
)
from flet_core.icons import REPORT, VERIFIED

from models.objects import Controller
from models.objects.marketplace import Listing, ListingStatus
from models.objects.user import User
from utils.functions import long_throttle, throttle, chunks

MARKET_MAX_SALE = 9999 * 9999 * 16


class MarketplaceSettings:
    selected_item = None
    create_category = None
    create_word = None
    create_amount = None
    create_price = None
    search_word = None
    listing_status = ListingStatus.listed
    ylistings_max_pages = 0
    ylistings_page = 0
    ylistings_per_page = 4
    ylistings_max_listings = 0


class MarketplaceController(Controller):
    def setup_controls(self):
        if not hasattr(self, "market"):
            self.items = self.page.trove_items
            self.categories = sorted(
                list(
                    set([i.category for i in self.items if i.category and i.marketable])
                )
            )
            self.market = MarketplaceSettings()
            self.main = ResponsiveRow(disabled=True)
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
                                                    not bool(
                                                        self.market.selected_item
                                                    )
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
                        horizontal_alignment="center"
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
                    col=4,
                )
            ]
        )
        asyncio.create_task(self.update_listings())
        asyncio.create_task(self.update_your_listings())
        self.main.controls.append(self.listings)

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
        listings = await Listing.find_many({}, limit=10, fetch_links=True).to_list(length=999999)
        self.market.ylistings_max_listings = len(listings)
        if not self.market.ylistings_max_listings:
            return
        listing_chunks = chunks(listings, self.market.ylistings_per_page)
        self.market.ylistings_max_pages = len(listing_chunks)
        if self.market.ylistings_page > self.market.ylistings_max_pages:
            self.market.ylistings_page = self.market.ylistings_max_pages
        if self.market.ylistings_page < 0:
            self.market.ylistings_page = 0
        for listing in listing_chunks[self.market.ylistings_page]:
            # Prevent listing others' listings
            if listing.seller.discord_id != int(self.page.discord_user.id):
                continue
            # Filter listings with bad status
            if listing.status != self.market.listing_status:
                continue
            self.your_listings.controls.append(
                Card(
                    content=Row(
                        controls=[
                            Image(src_base64=listing.item.icon_base64, width=125),
                            Column(
                                controls=[
                                    Container(
                                        Text(listing.item.name, color="cyan"),
                                        data=listing.item.trovesaurus_url,
                                        on_click=self.go_to_url,
                                        tooltip="Click me for more information"
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
                                                                Text(f"{listing.price:,}", size=12),
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                surface_tint_color="red"
                                            ),
                                            *[
                                                Text("or", size=12) if listing.price >= 150_000 else Text()
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
                                                                    f"{int(listing.better_price[0]):,}", size=12
                                                                ),
                                                                Image(
                                                                    src="assets/images/resources/item_crafting_spark.png",
                                                                    width=20,
                                                                ),
                                                                Text(
                                                                    f"{int(listing.better_price[1]):,}", size=12
                                                                ),
                                                            ]
                                                        )
                                                    ] if listing.price >= 150_000 else []
                                                ),
                                                surface_tint_color="red"
                                            )
                                        ]
                                    ),
                                    Row(
                                        controls=[
                                            Card(
                                                content=Row(
                                                    controls=[
                                                        Text("Quantity:", size=12),
                                                        Text(f"{listing.amount:,}", size=12)
                                                    ]
                                                ),
                                                surface_tint_color="red"
                                            ),
                                            Card(
                                                content=Row(
                                                    controls=[
                                                        Text("Price Each:", size=12),
                                                        Image(
                                                            src="assets/images/resources/item_crafting_spark.png",
                                                            width=20,
                                                        ),
                                                        Text(f"{listing.price_per:,g}", size=12)
                                                    ]
                                                ),
                                                surface_tint_color="red"
                                            )
                                        ]
                                    ),
                                    Row(
                                        controls=[
                                            ElevatedButton("Cancel", height=25),
                                            ElevatedButton("Relist", height=25),
                                        ],
                                        alignment=MainAxisAlignment.END
                                    ),
                                ],
                                spacing=2
                            ),
                        ]
                    ),
                    surface_tint_color="blue",
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 6, "xxl": 6},
                    margin=10
                )
            )
        self.your_listings.controls.extend(
            [
                ElevatedButton(
                    "Previous",
                    disabled=self.market.ylistings_max_pages == 1,
                    on_click=self.previous_your_listings,
                    col={"xs": 8, "sm": 4, "md": 4, "lg": 4, "xl": 2, "xxl": 2}
                ),
                Text(
                    f"Page {self.market.ylistings_page+1} of {self.market.ylistings_max_pages}",
                    text_align="center",
                    col={"xs": 4, "sm": 2, "md": 2, "lg": 2, "xl": 1, "xxl": 1}
                ),
                ElevatedButton(
                    "Next",
                    disabled=self.market.ylistings_max_pages == 1,
                    on_click=self.next_your_listings,
                    col={"xs": 8, "sm": 4, "md": 4, "lg": 4, "xl": 2, "xxl": 2}
                )
            ]
        )
        while True:
            await asyncio.sleep(1)
            try:
                await self.your_listings.update_async()
                break
            except Exception:
                ...

    def filter_items(self, item):
        if (
            self.market.create_category
            and item.category != self.market.create_category
        ):
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
                            "value": self.page.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Reported"},
                }
            ],
        }
        resp = requests.post(self.page.market_log_webhook, json=message)
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
                                    self.page.discord_user.username,
                                    self.page.discord_user.discriminator,
                                ]
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Reporter ID",
                            "value": self.page.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Reported"},
                }
            ],
        }
        resp = requests.post(self.page.market_log_webhook, json=message)
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
                                    self.page.discord_user.username,
                                    self.page.discord_user.discriminator,
                                ]
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Creator ID",
                            "value": self.page.discord_user.id,
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Created"},
                }
            ],
        }
        resp = requests.post(self.page.market_log_webhook, json=message)
        if resp.status_code == 204:
            user = await User.find_one(
                User.discord_id == int(self.page.discord_user.id)
            )
            listing = Listing(
                item=self.market.selected_item,
                seller=user,
                price=int(
                    self.market.create_amount
                    * self.market.create_price
                ),
                amount=self.market.create_price,
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
