from django.contrib import admin
from badge.models import *

admin.site.register(AwardedBadge)
admin.site.register(PerfectScoresOnCourseBadge)
admin.site.register(EarlySubmissionBadge)
admin.site.register(MinimumGradeOnRoundBadge)
admin.site.register(MetaBadge)
admin.site.register(BadgeUser)
admin.site.register(ToggleHistory)
