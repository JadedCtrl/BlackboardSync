"""
Blackboard Model Classes
"""

# Copyright (C) 2021, Jacob Sánchez Pérez

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from enum import Enum
from datetime import datetime

from pydantic import BaseModel, validator
from pathvalidate import sanitize_filename


class ImmutableModel(BaseModel):
    class Config:
        allow_mutation = False


class BBLocale(ImmutableModel):
    force: bool = False


class BBDurationType(str, Enum):
    Continuous: str = 'Continuous'
    DateRange: str = 'DateRange'
    FixedNumDays: str = 'FixedNumDays'
    Term: str = 'Term'


class BBDuration(ImmutableModel):
    type: str = None


class BBEnrollment(ImmutableModel):
    type: str = None


class BBProctoring(ImmutableModel):
    secureBrowserRequiredToTake: bool = False
    secureBrowserRequiredToReview: bool = False
    webcamRequired: bool = False


class BBFile(ImmutableModel):
    """Blackboard File."""
    fileName: str = None


class BBAttachment(ImmutableModel):
    """Blackboard File Attachment."""
    id: str = None
    fileName: str = None
    mimeType: str = None


class BBLink(ImmutableModel):
    """Blackboard Link."""
    href: str = None
    rel: str = None
    title: str = None
    type: str = None


class BBAvailability(ImmutableModel):
    available: bool = None
    allowGuests: bool = False
    adaptiveRelease: dict = {}
    duration: BBDuration


class BBMembership(ImmutableModel):
    """Blackboard Membership. Represents relation between student and course."""
    id: str = None
    userId: str = None
    courseId: str = None
    dataSourceId: str = None
    created: datetime = None
    modified: datetime = None
    availability: BBAvailability = None
    courseRoleId: str = None
    lastAccessed: datetime = None
    childCourseId: str = None


class BBResourceType(str, Enum):
    folder = 'x-bb-folder'
    file = 'x-bb-file'
    document = 'x-bb-document'
    externallink = 'x-bb-externallink'
    toollink = 'x-bb-toollink'
    turnitin_assignment = 'x-turnitin-assignment'
    bltiplacement_portal = 'x-bb-bltiplacement-Portal'
    assignment = 'x-bb-assignment'
    asmt_test_link = 'x-bb-asmt-test-link'
    syllabus = 'x-bb-syllabus'
    courselink = 'x-bb-courselink'
    blankpage = 'x-bb-blankpage'


class BBContentHandler(ImmutableModel):
    id: BBResourceType = None
    url: str = None
    file: BBFile = None
    gradeColumnId: str = None
    groupContent: str = None
    targetId: str = None
    targetType: str = None
    placementHandle: str = None
    assessmentId: str = None
    proctoring: BBProctoring = None

    @validator('id')
    def resource_parser(cls, v: str):
        return v.replace('resource/', '')

    @property
    def isNotHandled(self) -> bool:
        return self.id not in (BBResourceType.folder, BBResourceType.file,
                               BBResourceType.document, BBResourceType.externallink)


class BBCourseContent(ImmutableModel):
    """Blackboard Content."""
    id: str = None
    title: str = None
    body: str = None
    created: datetime = None
    modified: datetime = None
    position: int = 0
    hasChildren: bool = False
    launchInNewWindow: bool = False
    reviewable: bool = False
    availability: BBAvailability = None
    contentHandler: BBContentHandler = None
    links: list[BBLink] = []
    hasGradebookColumns: bool = False
    hasAssociatedGroups: bool = False

    def __str__(self):
        return self.title

    @property
    def title_path_safe(self) -> str:
        return sanitize_filename(self._title, replacement_text='_')


class BBContentChild(BBCourseContent):
    """Blackboard Content Child."""
    body: str = None
    parentId: str = None


class BBCourse(ImmutableModel):
    """BlackboardCourse. Represents an academic course."""

    _parse_name = True

    id: str = None
    courseId: str = None
    name: str = None
    description: str = None
    modified: datetime = None
    organization: bool = False
    ultraStatus: str = None
    closedComplete: bool = False
    availability: BBAvailability = None
    enrollment: BBEnrollment = None
    locale: BBLocale = None
    externalAccessUrl: str = None

    # Used by UCLan module names
    code: str = None
    title: str = None

    @validator('code')
    def code_parser(cls, v, values, **kwargs):
        if 'name' in values:
            code_split = values['name'].split(' : ', 1)
            return code_split[0]
        return v

    @validator('title')
    def title_parser(cls, v, values, **kwargs):
        if 'name' in values:
            name_split = values['name'].split(' : ', 1)[-1].split(',')
            return sanitize_filename(name_split[0], replacement_text='_')
        return v
