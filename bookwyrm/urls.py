""" url routing for the app and api """
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import TemplateView

from bookwyrm import settings, views
from bookwyrm.utils import regex

USER_PATH = rf"^user/(?P<username>{regex.USERNAME})"
LOCAL_USER_PATH = rf"^user/(?P<username>{regex.LOCALNAME})"

status_types = [
    "status",
    "review",
    "reviewrating",
    "comment",
    "quotation",
    "boost",
    "generatednote",
]

STATUS_TYPES_STRING = "|".join(status_types)
STATUS_PATH = rf"{USER_PATH}/({STATUS_TYPES_STRING})/(?P<status_id>\d+)"

BOOK_PATH = r"^book/(?P<book_id>\d+)"

STREAMS = "|".join(s["key"] for s in settings.STREAMS)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    # federation endpoints
    re_path(r"^inbox/?$", views.Inbox.as_view()),
    re_path(rf"{LOCAL_USER_PATH}/inbox/?$", views.Inbox.as_view()),
    re_path(rf"{LOCAL_USER_PATH}/outbox/?$", views.Outbox.as_view()),
    re_path(r"^\.well-known/webfinger/?$", views.webfinger),
    re_path(r"^\.well-known/nodeinfo/?$", views.nodeinfo_pointer),
    re_path(r"^\.well-known/host-meta/?$", views.host_meta),
    re_path(r"^nodeinfo/2\.0/?$", views.nodeinfo),
    re_path(r"^api/v1/instance/?$", views.instance_info),
    re_path(r"^api/v1/instance/peers/?$", views.peers),
    re_path(r"^opensearch.xml$", views.opensearch, name="opensearch"),
    # polling updates
    re_path("^api/updates/notifications/?$", views.get_notification_count),
    re_path("^api/updates/stream/(?P<stream>[a-z]+)/?$", views.get_unread_status_count),
    # authentication
    re_path(r"^login/?$", views.Login.as_view(), name="login"),
    re_path(r"^login/(?P<confirmed>confirmed)?$", views.Login.as_view(), name="login"),
    re_path(r"^register/?$", views.Register.as_view()),
    re_path(r"confirm-email/?$", views.ConfirmEmail.as_view(), name="confirm-email"),
    re_path(
        r"confirm-email/(?P<code>[A-Za-z0-9]+)/?$",
        views.ConfirmEmailCode.as_view(),
        name="confirm-email-code",
    ),
    re_path(r"^resend-link/?$", views.resend_link, name="resend-link"),
    re_path(r"^logout/?$", views.Logout.as_view(), name="logout"),
    re_path(
        r"^password-reset/?$",
        views.PasswordResetRequest.as_view(),
        name="password-reset",
    ),
    re_path(
        r"^password-reset/(?P<code>[A-Za-z0-9]+)/?$", views.PasswordReset.as_view()
    ),
    # admin
    re_path(
        r"^settings/dashboard/?$", views.Dashboard.as_view(), name="settings-dashboard"
    ),
    re_path(r"^settings/site-settings/?$", views.Site.as_view(), name="settings-site"),
    re_path(
        r"^settings/announcements/?$",
        views.Announcements.as_view(),
        name="settings-announcements",
    ),
    re_path(
        r"^settings/announcements/(?P<announcement_id>\d+)/?$",
        views.Announcement.as_view(),
        name="settings-announcements",
    ),
    re_path(
        r"^settings/announcements/(?P<announcement_id>\d+)/delete/?$",
        views.delete_announcement,
        name="settings-announcements-delete",
    ),
    re_path(
        r"^settings/email-preview/?$",
        views.admin.site.email_preview,
        name="settings-email-preview",
    ),
    re_path(
        r"^settings/users/?$", views.UserAdminList.as_view(), name="settings-users"
    ),
    re_path(
        r"^settings/users/(?P<user>\d+)/?$",
        views.UserAdmin.as_view(),
        name="settings-user",
    ),
    re_path(
        r"^settings/federation/(?P<status>(federated|blocked))?/?$",
        views.Federation.as_view(),
        name="settings-federation",
    ),
    re_path(
        r"^settings/federation/(?P<server>\d+)/?$",
        views.FederatedServer.as_view(),
        name="settings-federated-server",
    ),
    re_path(
        r"^settings/federation/(?P<server>\d+)/block?$",
        views.block_server,
        name="settings-federated-server-block",
    ),
    re_path(
        r"^settings/federation/(?P<server>\d+)/unblock?$",
        views.unblock_server,
        name="settings-federated-server-unblock",
    ),
    re_path(
        r"^settings/federation/add/?$",
        views.AddFederatedServer.as_view(),
        name="settings-add-federated-server",
    ),
    re_path(
        r"^settings/federation/import/?$",
        views.ImportServerBlocklist.as_view(),
        name="settings-import-blocklist",
    ),
    re_path(
        r"^settings/invites/?$", views.ManageInvites.as_view(), name="settings-invites"
    ),
    re_path(
        r"^settings/requests/?$",
        views.ManageInviteRequests.as_view(),
        name="settings-invite-requests",
    ),
    re_path(
        r"^settings/requests/ignore?$",
        views.ignore_invite_request,
        name="settings-invite-requests-ignore",
    ),
    re_path(
        r"^invite-request/?$", views.InviteRequest.as_view(), name="invite-request"
    ),
    re_path(r"^invite/(?P<code>[A-Za-z0-9]+)/?$", views.Invite.as_view()),
    re_path(
        r"^settings/email-blocklist/?$",
        views.EmailBlocklist.as_view(),
        name="settings-email-blocks",
    ),
    re_path(
        r"^settings/email-blocks/(?P<domain_id>\d+)/delete/?$",
        views.EmailBlocklist.as_view(),
        name="settings-email-blocks-delete",
    ),
    re_path(
        r"^settings/ip-blocklist/?$",
        views.IPBlocklist.as_view(),
        name="settings-ip-blocks",
    ),
    re_path(
        r"^settings/ip-blocks/(?P<block_id>\d+)/delete/?$",
        views.IPBlocklist.as_view(),
        name="settings-ip-blocks-delete",
    ),
    # moderation
    re_path(r"^settings/reports/?$", views.Reports.as_view(), name="settings-reports"),
    re_path(
        r"^settings/reports/(?P<report_id>\d+)/?$",
        views.Report.as_view(),
        name="settings-report",
    ),
    re_path(
        r"^settings/reports/(?P<user_id>\d+)/suspend/?$",
        views.suspend_user,
        name="settings-report-suspend",
    ),
    re_path(
        r"^settings/reports/(?P<user_id>\d+)/unsuspend/?$",
        views.unsuspend_user,
        name="settings-report-unsuspend",
    ),
    re_path(
        r"^settings/reports/(?P<user_id>\d+)/delete/?$",
        views.moderator_delete_user,
        name="settings-delete-user",
    ),
    re_path(
        r"^settings/reports/(?P<report_id>\d+)/resolve/?$",
        views.resolve_report,
        name="settings-report-resolve",
    ),
    re_path(r"^report/?$", views.make_report, name="report"),
    # landing pages
    re_path(r"^about/?$", views.About.as_view(), name="about"),
    path("", views.Home.as_view(), name="landing"),
    re_path(r"^discover/?$", views.Discover.as_view(), name="discover"),
    re_path(r"^notifications/?$", views.Notifications.as_view(), name="notifications"),
    re_path(
        r"^notifications/(?P<notification_type>mentions)/?$",
        views.Notifications.as_view(),
        name="notifications",
    ),
    re_path(r"^directory/?", views.Directory.as_view(), name="directory"),
    # Get started
    re_path(
        r"^get-started/profile/?$",
        views.GetStartedProfile.as_view(),
        name="get-started-profile",
    ),
    re_path(
        r"^get-started/books/?$",
        views.GetStartedBooks.as_view(),
        name="get-started-books",
    ),
    re_path(
        r"^get-started/users/?$",
        views.GetStartedUsers.as_view(),
        name="get-started-users",
    ),
    # feeds
    re_path(rf"^(?P<tab>{STREAMS})/?$", views.Feed.as_view()),
    re_path(
        r"^direct-messages/?$", views.DirectMessage.as_view(), name="direct-messages"
    ),
    re_path(
        rf"^direct-messages/(?P<username>{regex.USERNAME})?$",
        views.DirectMessage.as_view(),
        name="direct-messages-user",
    ),
    # search
    re_path(r"^search.json/?$", views.Search.as_view(), name="search"),
    re_path(r"^search/?$", views.Search.as_view(), name="search"),
    # imports
    re_path(r"^import/?$", views.Import.as_view(), name="import"),
    re_path(r"^import/(\d+)/?$", views.ImportStatus.as_view(), name="import-status"),
    # users
    re_path(rf"{USER_PATH}\.json$", views.User.as_view()),
    re_path(rf"{USER_PATH}/?$", views.User.as_view(), name="user-feed"),
    re_path(rf"{USER_PATH}/rss/?$", views.rss_feed.RssFeed(), name="user-rss"),
    re_path(
        rf"{USER_PATH}/followers(.json)?/?$",
        views.Followers.as_view(),
        name="user-followers",
    ),
    re_path(
        rf"{USER_PATH}/following(.json)?/?$",
        views.Following.as_view(),
        name="user-following",
    ),
    re_path(r"^hide-suggestions/?$", views.hide_suggestions, name="hide-suggestions"),
    # lists
    re_path(rf"{USER_PATH}/lists/?$", views.UserLists.as_view(), name="user-lists"),
    re_path(r"^list/?$", views.Lists.as_view(), name="lists"),
    re_path(r"^list/saved/?$", views.SavedLists.as_view(), name="saved-lists"),
    re_path(r"^list/(?P<list_id>\d+)(.json)?/?$", views.List.as_view(), name="list"),
    re_path(r"^list/delete/(?P<list_id>\d+)/?$", views.delete_list, name="delete-list"),
    re_path(r"^list/add-book/?$", views.list.add_book, name="list-add-book"),
    re_path(
        r"^list/(?P<list_id>\d+)/remove/?$",
        views.list.remove_book,
        name="list-remove-book",
    ),
    re_path(
        r"^list-item/(?P<list_item_id>\d+)/set-position$",
        views.list.set_book_position,
        name="list-set-book-position",
    ),
    re_path(
        r"^list/(?P<list_id>\d+)/curate/?$", views.Curate.as_view(), name="list-curate"
    ),
    re_path(r"^save-list/(?P<list_id>\d+)/?$", views.save_list, name="list-save"),
    re_path(r"^unsave-list/(?P<list_id>\d+)/?$", views.unsave_list, name="list-unsave"),
    # User books
    re_path(rf"{USER_PATH}/books/?$", views.Shelf.as_view(), name="user-shelves"),
    re_path(
        rf"^{USER_PATH}/(shelf|books)/(?P<shelf_identifier>[\w-]+)(.json)?/?$",
        views.Shelf.as_view(),
        name="shelf",
    ),
    re_path(
        rf"^{LOCAL_USER_PATH}/(books|shelf)/(?P<shelf_identifier>[\w-]+)(.json)?/?$",
        views.Shelf.as_view(),
        name="shelf",
    ),
    re_path(r"^create-shelf/?$", views.create_shelf, name="shelf-create"),
    re_path(r"^delete-shelf/(?P<shelf_id>\d+)?$", views.delete_shelf),
    re_path(r"^shelve/?$", views.shelve),
    re_path(r"^unshelve/?$", views.unshelve),
    # goals
    re_path(
        rf"{LOCAL_USER_PATH}/goal/(?P<year>\d+)/?$",
        views.Goal.as_view(),
        name="user-goal",
    ),
    re_path(r"^hide-goal/?$", views.hide_goal, name="hide-goal"),
    # preferences
    re_path(r"^preferences/profile/?$", views.EditUser.as_view(), name="prefs-profile"),
    re_path(
        r"^preferences/password/?$",
        views.ChangePassword.as_view(),
        name="prefs-password",
    ),
    re_path(r"^preferences/delete/?$", views.DeleteUser.as_view(), name="prefs-delete"),
    re_path(r"^preferences/block/?$", views.Block.as_view(), name="prefs-block"),
    re_path(r"^block/(?P<user_id>\d+)/?$", views.Block.as_view()),
    re_path(r"^unblock/(?P<user_id>\d+)/?$", views.unblock),
    # statuses
    re_path(rf"{STATUS_PATH}(.json)?/?$", views.Status.as_view(), name="status"),
    re_path(rf"{STATUS_PATH}/activity/?$", views.Status.as_view(), name="status"),
    re_path(
        rf"{STATUS_PATH}/replies(.json)?/?$", views.Replies.as_view(), name="replies"
    ),
    re_path(
        r"^edit/(?P<status_id>\d+)/?$", views.EditStatus.as_view(), name="edit-status"
    ),
    re_path(
        r"^post/?$",
        views.CreateStatus.as_view(),
        name="create-status",
    ),
    re_path(
        r"^post/(?P<status_type>\w+)/?$",
        views.CreateStatus.as_view(),
        name="create-status",
    ),
    re_path(
        r"^post/(?P<status_type>\w+)/(?P<existing_status_id>\d+)/?$",
        views.CreateStatus.as_view(),
        name="create-status",
    ),
    re_path(
        r"^delete-status/(?P<status_id>\d+)/?$",
        views.DeleteStatus.as_view(),
        name="delete-status",
    ),
    # interact
    re_path(r"^favorite/(?P<status_id>\d+)/?$", views.Favorite.as_view(), name="fav"),
    re_path(
        r"^unfavorite/(?P<status_id>\d+)/?$", views.Unfavorite.as_view(), name="unfav"
    ),
    re_path(r"^boost/(?P<status_id>\d+)/?$", views.Boost.as_view()),
    re_path(r"^unboost/(?P<status_id>\d+)/?$", views.Unboost.as_view()),
    # books
    re_path(rf"{BOOK_PATH}(.json)?/?$", views.Book.as_view(), name="book"),
    re_path(
        rf"{BOOK_PATH}/(?P<user_statuses>review|comment|quote)/?$",
        views.Book.as_view(),
        name="book-user-statuses",
    ),
    re_path(rf"{BOOK_PATH}/edit/?$", views.EditBook.as_view(), name="edit-book"),
    re_path(rf"{BOOK_PATH}/confirm/?$", views.ConfirmEditBook.as_view()),
    re_path(r"^create-book/?$", views.EditBook.as_view(), name="create-book"),
    re_path(r"^create-book/confirm?$", views.ConfirmEditBook.as_view()),
    re_path(rf"{BOOK_PATH}/editions(.json)?/?$", views.Editions.as_view()),
    re_path(
        r"^upload-cover/(?P<book_id>\d+)/?$", views.upload_cover, name="upload-cover"
    ),
    re_path(r"^add-description/(?P<book_id>\d+)/?$", views.add_description),
    re_path(r"^resolve-book/?$", views.resolve_book),
    re_path(r"^switch-edition/?$", views.switch_edition),
    # isbn
    re_path(r"^isbn/(?P<isbn>\d+)(.json)?/?$", views.Isbn.as_view()),
    # author
    re_path(r"^author/(?P<author_id>\d+)(.json)?/?$", views.Author.as_view()),
    re_path(r"^author/(?P<author_id>\d+)/edit/?$", views.EditAuthor.as_view()),
    # reading progress
    re_path(r"^edit-readthrough/?$", views.edit_readthrough, name="edit-readthrough"),
    re_path(r"^delete-readthrough/?$", views.delete_readthrough),
    re_path(r"^create-readthrough/?$", views.create_readthrough),
    re_path(r"^delete-progressupdate/?$", views.delete_progressupdate),
    # shelve actions
    re_path(
        r"^reading-status/update/(?P<book_id>\d+)/?$",
        views.update_progress,
        name="reading-status-update",
    ),
    re_path(
        r"^reading-status/(?P<status>want|start|finish)/(?P<book_id>\d+)/?$",
        views.ReadingStatus.as_view(),
        name="reading-status",
    ),
    # following
    re_path(r"^follow/?$", views.follow, name="follow"),
    re_path(r"^unfollow/?$", views.unfollow, name="unfollow"),
    re_path(r"^accept-follow-request/?$", views.accept_follow_request),
    re_path(r"^delete-follow-request/?$", views.delete_follow_request),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
