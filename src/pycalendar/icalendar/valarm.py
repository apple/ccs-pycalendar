##
#    Copyright (c) 2007-2013 Cyrus Daboo. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##

from pycalendar.parameter import Parameter
from pycalendar.datetime import DateTime
from pycalendar.duration import Duration
from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.value import Value

class VAlarm(Component):

    sActionMap = {
        definitions.cICalProperty_ACTION_AUDIO: definitions.eAction_VAlarm_Audio,
        definitions.cICalProperty_ACTION_DISPLAY: definitions.eAction_VAlarm_Display,
        definitions.cICalProperty_ACTION_EMAIL: definitions.eAction_VAlarm_Email,
        definitions.cICalProperty_ACTION_PROCEDURE: definitions.eAction_VAlarm_Procedure,
        definitions.cICalProperty_ACTION_URI: definitions.eAction_VAlarm_URI,
        definitions.cICalProperty_ACTION_NONE: definitions.eAction_VAlarm_None,
    }

    sActionValueMap = {
        definitions.eAction_VAlarm_Audio: definitions.cICalProperty_ACTION_AUDIO,
        definitions.eAction_VAlarm_Display: definitions.cICalProperty_ACTION_DISPLAY,
        definitions.eAction_VAlarm_Email: definitions.cICalProperty_ACTION_EMAIL,
        definitions.eAction_VAlarm_Procedure: definitions.cICalProperty_ACTION_PROCEDURE,
        definitions.eAction_VAlarm_URI: definitions.cICalProperty_ACTION_URI,
        definitions.eAction_VAlarm_None: definitions.cICalProperty_ACTION_NONE,
    }

    # Classes for each action encapsulating action-specific data
    class VAlarmAction(object):

        propertyCardinality_1 = ()
        propertyCardinality_1_Fix_Empty = ()
        propertyCardinality_0_1 = ()
        propertyCardinality_1_More = ()

        def __init__(self, type):
            self.mType = type

        def duplicate(self):
            return VAlarm.VAlarmAction(self.mType)

        def load(self, valarm):
            pass

        def add(self, valarm):
            pass

        def remove(self, valarm):
            pass

        def getType(self):
            return self.mType


    class VAlarmAudio(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
            definitions.cICalProperty_TRIGGER,
        )

        propertyCardinality_0_1 = (
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_REPEAT,
            definitions.cICalProperty_ATTACH,
            definitions.cICalProperty_ACKNOWLEDGED,
        )

        def __init__(self, speak=None):
            super(VAlarm.VAlarmAudio, self).__init__(type=definitions.eAction_VAlarm_Audio)
            self.mSpeakText = speak

        def duplicate(self):
            return VAlarm.VAlarmAudio(self.mSpeakText)

        def load(self, valarm):
            # Get properties
            self.mSpeakText = valarm.loadValueString(definitions.cICalProperty_ACTION_X_SPEAKTEXT)

        def add(self, valarm):
            # Delete existing then add
            self.remove(valarm)

            prop = Property(definitions.cICalProperty_ACTION_X_SPEAKTEXT, self.mSpeakText)
            valarm.addProperty(prop)

        def remove(self, valarm):
            valarm.removeProperties(definitions.cICalProperty_ACTION_X_SPEAKTEXT)

        def isSpeakText(self):
            return len(self.mSpeakText) != 0

        def getSpeakText(self):
            return self.mSpeakText


    class VAlarmDisplay(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
            definitions.cICalProperty_TRIGGER,
        )

        propertyCardinality_1_Fix_Empty = (
            definitions.cICalProperty_DESCRIPTION,
        )

        propertyCardinality_0_1 = (
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_REPEAT,
            definitions.cICalProperty_ACKNOWLEDGED,
        )

        def __init__(self, description=None):
            super(VAlarm.VAlarmDisplay, self).__init__(type=definitions.eAction_VAlarm_Display)
            self.mDescription = description

        def duplicate(self):
            return VAlarm.VAlarmDisplay(self.mDescription)

        def load(self, valarm):
            # Get properties
            self.mDescription = valarm.loadValueString(definitions.cICalProperty_DESCRIPTION)

        def add(self, valarm):
            # Delete existing then add
            self.remove(valarm)

            prop = Property(definitions.cICalProperty_DESCRIPTION, self.mDescription)
            valarm.addProperty(prop)

        def remove(self, valarm):
            valarm.removeProperties(definitions.cICalProperty_DESCRIPTION)

        def getDescription(self):
            return self.mDescription


    class VAlarmEmail(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
            definitions.cICalProperty_TRIGGER,
        )

        propertyCardinality_1_Fix_Empty = (
            definitions.cICalProperty_DESCRIPTION,
            definitions.cICalProperty_SUMMARY,
        )

        propertyCardinality_0_1 = (
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_REPEAT,
            definitions.cICalProperty_ACKNOWLEDGED,
        )

        propertyCardinality_1_More = (
            definitions.cICalProperty_ATTENDEE,
        )

        def __init__(self, description=None, summary=None, attendees=None):
            super(VAlarm.VAlarmEmail, self).__init__(type=definitions.eAction_VAlarm_Email)
            self.mDescription = description
            self.mSummary = summary
            self.mAttendees = attendees

        def duplicate(self):
            return VAlarm.VAlarmEmail(self.mDescription, self.mSummary, self.mAttendees)

        def load(self, valarm):
            # Get properties
            self.mDescription = valarm.loadValueString(definitions.cICalProperty_DESCRIPTION)
            self.mSummary = valarm.loadValueString(definitions.cICalProperty_SUMMARY)

            self.mAttendees = []
            if valarm.hasProperty(definitions.cICalProperty_ATTENDEE):
                # Get each attendee
                range = valarm.getProperties().get(definitions.cICalProperty_ATTENDEE, ())
                for iter in range:
                    # Get the attendee value
                    attendee = iter.getCalAddressValue()
                    if attendee is not None:
                        self.mAttendees.append(attendee.getValue())

        def add(self, valarm):
            # Delete existing then add
            self.remove(valarm)

            prop = Property(definitions.cICalProperty_DESCRIPTION, self.mDescription)
            valarm.addProperty(prop)

            prop = Property(definitions.cICalProperty_SUMMARY, self.mSummary)
            valarm.addProperty(prop)

            for iter in self.mAttendees:
                prop = Property(definitions.cICalProperty_ATTENDEE, iter, Value.VALUETYPE_CALADDRESS)
                valarm.addProperty(prop)

        def remove(self, valarm):
            valarm.removeProperties(definitions.cICalProperty_DESCRIPTION)
            valarm.removeProperties(definitions.cICalProperty_SUMMARY)
            valarm.removeProperties(definitions.cICalProperty_ATTENDEE)

        def getDescription(self):
            return self.mDescription

        def getSummary(self):
            return self.mSummary

        def getAttendees(self):
            return self.mAttendees


    class VAlarmUnknown(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
            definitions.cICalProperty_TRIGGER,
        )

        propertyCardinality_0_1 = (
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_REPEAT,
            definitions.cICalProperty_ACKNOWLEDGED,
        )

        def __init__(self):
            super(VAlarm.VAlarmUnknown, self).__init__(type=definitions.eAction_VAlarm_Unknown)

        def duplicate(self):
            return VAlarm.VAlarmUnknown()


    class VAlarmURI(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
            definitions.cICalProperty_TRIGGER,
            definitions.cICalProperty_URL,
        )

        propertyCardinality_0_1 = (
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_REPEAT,
            definitions.cICalProperty_ACKNOWLEDGED,
        )

        def __init__(self, uri=None):
            super(VAlarm.VAlarmURI, self).__init__(type=definitions.eAction_VAlarm_URI)
            self.mURI = uri

        def duplicate(self):
            return VAlarm.VAlarmURI(self.mURI)

        def load(self, valarm):
            # Get properties
            self.mURI = valarm.loadValueString(definitions.cICalProperty_URL)

        def add(self, valarm):
            # Delete existing then add
            self.remove(valarm)

            prop = Property(definitions.cICalProperty_URL, self.mURI)
            valarm.addProperty(prop)

        def remove(self, valarm):
            valarm.removeProperties(definitions.cICalProperty_URL)

        def getURI(self):
            return self.mURI


    class VAlarmNone(VAlarmAction):

        propertyCardinality_1 = (
            definitions.cICalProperty_ACTION,
        )

        def __init__(self):
            super(VAlarm.VAlarmNone, self).__init__(type=definitions.eAction_VAlarm_None)

        def duplicate(self):
            return VAlarm.VAlarmNone()


    def getMimeComponentName(self):
        # Cannot be sent as a separate MIME object
        return None

    sActionToAlarmMap = {
        definitions.eAction_VAlarm_Audio: VAlarmAudio,
        definitions.eAction_VAlarm_Display: VAlarmDisplay,
        definitions.eAction_VAlarm_Email: VAlarmEmail,
        definitions.eAction_VAlarm_URI: VAlarmURI,
        definitions.eAction_VAlarm_None: VAlarmNone,
    }

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):

        super(VAlarm, self).__init__(parent=parent)

        self.mAction = definitions.eAction_VAlarm_Display
        self.mTriggerAbsolute = False
        self.mTriggerOnStart = True
        self.mTriggerOn = DateTime()

        # Set duration default to 1 hour
        self.mTriggerBy = Duration()
        self.mTriggerBy.setDuration(60 * 60)

        # Does not repeat by default
        self.mRepeats = 0
        self.mRepeatInterval = Duration()
        self.mRepeatInterval.setDuration(5 * 60) # Five minutes

        # Status
        self.mStatusInit = False
        self.mAlarmStatus = definitions.eAlarm_Status_Pending
        self.mLastTrigger = DateTime()
        self.mNextTrigger = DateTime()
        self.mDoneCount = 0

        # Create action data
        self.mActionData = VAlarm.VAlarmDisplay("")


    def duplicate(self, parent=None):
        other = super(VAlarm, self).duplicate(parent=parent)
        other.mAction = self.mAction
        other.mTriggerAbsolute = self.mTriggerAbsolute
        other.mTriggerOn = self.mTriggerOn.duplicate()
        other.mTriggerBy = self.mTriggerBy.duplicate()
        other.mTriggerOnStart = self.mTriggerOnStart

        other.mRepeats = self.mRepeats
        other.mRepeatInterval = self.mRepeatInterval.duplicate()

        other.mAlarmStatus = self.mAlarmStatus
        if self.mLastTrigger is not None:
            other.mLastTrigger = self.mLastTrigger.duplicate()
        if self.mNextTrigger is not None:
            other.mNextTrigger = self.mNextTrigger.duplicate()
        other.mDoneCount = self.mDoneCount

        other.mActionData = self.mActionData.duplicate()
        return other


    def getType(self):
        return definitions.cICalComponent_VALARM


    def getAction(self):
        return self.mAction


    def getActionData(self):
        return self.mActionData


    def isTriggerAbsolute(self):
        return self.mTriggerAbsolute


    def getTriggerOn(self):
        return self.mTriggerOn


    def getTriggerDuration(self):
        return self.mTriggerBy


    def isTriggerOnStart(self):
        return self.mTriggerOnStart


    def getRepeats(self):
        return self.mRepeats


    def getInterval(self):
        return self.mRepeatInterval


    def added(self):
        # Added to calendar so add to calendar notifier
        # calstore::CCalendarNotifier::sCalendarNotifier.AddAlarm(this)

        # Do inherited
        super(VAlarm, self).added()


    def removed(self):
        # Removed from calendar so add to calendar notifier
        # calstore::CCalendarNotifier::sCalendarNotifier.RemoveAlarm(this)

        # Do inherited
        super(VAlarm, self).removed()


    def changed(self):
        # Always force recalc of trigger status
        self.mStatusInit = False

        # Changed in calendar so change in calendar notifier
        # calstore::CCalendarNotifier::sCalendarNotifier.ChangedAlarm(this)

        # Do not do inherited as this is always a sub-component and we do not
        # do top-level component changes
        # super.changed()


    def finalise(self):
        # Do inherited
        super(VAlarm, self).finalise()

        # Get the ACTION
        temp = self.loadValueString(definitions.cICalProperty_ACTION)
        if temp is not None:
            self.mAction = VAlarm.sActionMap.get(temp, definitions.eAction_VAlarm_Unknown)
            self.loadAction()

        # Get the trigger
        if self.hasProperty(definitions.cICalProperty_TRIGGER):
            # Determine the type of the value
            temp1 = self.loadValueDateTime(definitions.cICalProperty_TRIGGER)
            temp2 = self.loadValueDuration(definitions.cICalProperty_TRIGGER)
            if temp1 is not None:
                self.mTriggerAbsolute = True
                self.mTriggerOn = temp1
            elif temp2 is not None:
                self.mTriggerAbsolute = False
                self.mTriggerBy = temp2

                # Get the property
                prop = self.findFirstProperty(definitions.cICalProperty_TRIGGER)

                # Look for RELATED parameter
                if prop.hasParameter(definitions.cICalParameter_RELATED):
                    temp = prop.getParameterValue(definitions.cICalParameter_RELATED)
                    if temp == definitions.cICalParameter_RELATED_START:
                        self.mTriggerOnStart = True
                    elif temp == definitions.cICalParameter_RELATED_END:
                        self.mTriggerOnStart = False
                else:
                    self.mTriggerOnStart = True

        # Get repeat & interval
        temp = self.loadValueInteger(definitions.cICalProperty_REPEAT)
        if temp is not None:
            self.mRepeats = temp
        temp = self.loadValueDuration(definitions.cICalProperty_DURATION)
        if temp is not None:
            self.mRepeatInterval = temp

        # Set a map key for sorting
        self.mMapKey = "%s:%s" % (self.mAction, self.mTriggerOn if self.mTriggerAbsolute else self.mTriggerBy,)

        # Alarm status - private to Mulberry
        status = self.loadValueString(definitions.cICalProperty_ALARM_X_ALARMSTATUS)
        if status is not None:
            if status == definitions.cICalProperty_ALARM_X_ALARMSTATUS_PENDING:
                self.mAlarmStatus = definitions.eAlarm_Status_Pending
            elif status == definitions.cICalProperty_ALARM_X_ALARMSTATUS_COMPLETED:
                self.mAlarmStatus = definitions.eAlarm_Status_Completed
            elif status == definitions.cICalProperty_ALARM_X_ALARMSTATUS_DISABLED:
                self.mAlarmStatus = definitions.eAlarm_Status_Disabled
            else:
                self.mAlarmStatus = definitions.eAlarm_Status_Pending

        # Last trigger time - private to Mulberry
        temp = self.loadValueDateTime(definitions.cICalProperty_ALARM_X_LASTTRIGGER)
        if temp is not None:
            self.mLastTrigger = temp


    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that.
        """

        # Validate using action specific constraints
        self.propertyCardinality_1 = self.mActionData.propertyCardinality_1
        self.propertyCardinality_1_Fix_Empty = self.mActionData.propertyCardinality_1_Fix_Empty
        self.propertyCardinality_0_1 = self.mActionData.propertyCardinality_0_1
        self.propertyCardinality_1_More = self.mActionData.propertyCardinality_1_More

        fixed, unfixed = super(VAlarm, self).validate(doFix)

        # Extra constraint: both DURATION and REPEAT must be present togethe
        if self.hasProperty(definitions.cICalProperty_DURATION) ^ self.hasProperty(definitions.cICalProperty_REPEAT):
            # Cannot fix this
            logProblem = "[%s] Properties must be present together: %s, %s" % (
                self.getType(),
                definitions.cICalProperty_DURATION,
                definitions.cICalProperty_REPEAT,
            )
            unfixed.append(logProblem)

        return fixed, unfixed


    def editStatus(self, status):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_ALARM_X_ALARMSTATUS)

        # Updated cached values
        self.mAlarmStatus = status

        # Add new
        status_txt = ""
        if self.mAlarmStatus == definitions.eAlarm_Status_Pending:
            status_txt = definitions.cICalProperty_ALARM_X_ALARMSTATUS_PENDING
        elif self.mAlarmStatus == definitions.eAlarm_Status_Completed:
            status_txt = definitions.cICalProperty_ALARM_X_ALARMSTATUS_COMPLETED
        elif self.mAlarmStatus == definitions.eAlarm_Status_Disabled:
            status_txt = definitions.cICalProperty_ALARM_X_ALARMSTATUS_DISABLED
        self.addProperty(Property(definitions.cICalProperty_ALARM_X_ALARMSTATUS, status_txt))


    def editAction(self, action, data):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_ACTION)
        self.mActionData.remove(self)
        self.mActionData = None

        # Updated cached values
        self.mAction = action
        self.mActionData = data

        # Add new properties to alarm
        action_txt = VAlarm.sActionValueMap.get(self.mAction, definitions.cICalProperty_ACTION_PROCEDURE)

        prop = Property(definitions.cICalProperty_ACTION, action_txt)
        self.addProperty(prop)

        self.mActionData.add(self)


    def editTriggerOn(self, dt):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_TRIGGER)

        # Updated cached values
        self.mTriggerAbsolute = True
        self.mTriggerOn = dt

        # Add new
        prop = Property(definitions.cICalProperty_TRIGGER, dt)
        self.addProperty(prop)


    def editTriggerBy(self, duration, trigger_start):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_TRIGGER)

        # Updated cached values
        self.mTriggerAbsolute = False
        self.mTriggerBy = duration
        self.mTriggerOnStart = trigger_start

        # Add new (with parameter)
        prop = Property(definitions.cICalProperty_TRIGGER, duration)
        attr = Parameter(definitions.cICalParameter_RELATED,
                 (definitions.cICalParameter_RELATED_START,
                  definitions.cICalParameter_RELATED_END)[not trigger_start])
        prop.addParameter(attr)
        self.addProperty(prop)


    def editRepeats(self, repeat, interval):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_REPEAT)
        self.removeProperties(definitions.cICalProperty_DURATION)

        # Updated cached values
        self.mRepeats = repeat
        self.mRepeatInterval = interval

        # Add new
        if self.mRepeats > 0:
            self.addProperty(Property(definitions.cICalProperty_REPEAT, repeat))
            self.addProperty(Property(definitions.cICalProperty_DURATION, interval))


    def getAlarmStatus(self):
        return self.mAlarmStatus


    def getNextTrigger(self, dt):
        if not self.mStatusInit:
            self.initNextTrigger()
        dt.copy(self.mNextTrigger)


    def alarmTriggered(self, dt):
        # Remove existing
        self.removeProperties(definitions.cICalProperty_ALARM_X_LASTTRIGGER)
        self.removeProperties(definitions.cICalProperty_ALARM_X_ALARMSTATUS)

        # Updated cached values
        self.mLastTrigger.copy(dt)

        if self.mDoneCount < self.mRepeats:
            self.mNextTrigger = self.mLastTrigger + self.mRepeatInterval
            dt.copy(self.mNextTrigger)
            self.mDoneCount += 1
            self.mAlarmStatus = definitions.eAlarm_Status_Pending
        else:
            self.mAlarmStatus = definitions.eAlarm_Status_Completed

        # Add new
        self.addProperty(Property(definitions.cICalProperty_ALARM_X_LASTTRIGGER, dt))
        status = ""
        if self.mAlarmStatus == definitions.eAlarm_Status_Pending:
            status = definitions.cICalProperty_ALARM_X_ALARMSTATUS_PENDING
        elif self.mAlarmStatus == definitions.eAlarm_Status_Completed:
            status = definitions.cICalProperty_ALARM_X_ALARMSTATUS_COMPLETED
        elif self.mAlarmStatus == definitions.eAlarm_Status_Disabled:
            status = definitions.cICalProperty_ALARM_X_ALARMSTATUS_DISABLED
        self.addProperty(Property(definitions.cICalProperty_ALARM_X_ALARMSTATUS, status))

        # Now update dt to the next alarm time
        return self.mAlarmStatus == definitions.eAlarm_Status_Pending


    def loadAction(self):
        # Delete current one
        self.mActionData = None
        self.mActionData = VAlarm.sActionToAlarmMap.get(self.mAction, VAlarm.VAlarmUnknown)()
        self.mActionData.load(self)


    def initNextTrigger(self):
        # Do not bother if its completed
        if self.mAlarmStatus == definitions.eAlarm_Status_Completed:
            return
        self.mStatusInit = True

        # Look for trigger immediately preceeding or equal to utc now
        nowutc = DateTime.getNowUTC()

        # Init done counter
        self.mDoneCount = 0

        # Determine the first trigger
        trigger = DateTime()
        self.getFirstTrigger(trigger)

        while self.mDoneCount < self.mRepeats:
            # See if next trigger is later than now
            next_trigger = trigger + self.mRepeatInterval
            if next_trigger > nowutc:
                break
            self.mDoneCount += 1
            trigger = next_trigger

        # Check for completion
        if trigger == self.mLastTrigger or (nowutc - trigger).getTotalSeconds() > 24 * 60 * 60:
            if self.mDoneCount == self.mRepeats:
                self.mAlarmStatus = definitions.eAlarm_Status_Completed
                return
            else:
                trigger = trigger + self.mRepeatInterval
                self.mDoneCount += 1

        self.mNextTrigger = trigger


    def getFirstTrigger(self, dt):
        # If absolute trigger, use that
        if self.isTriggerAbsolute():
            # Get the trigger on
            dt.copy(self.getTriggerOn())
        else:
            # Get the parent embedder class (must be CICalendarComponentRecur type)
            owner = self.getEmbedder()
            if owner is not None:
                # Determine time at which alarm will trigger
                trigger = (owner.getStart(), owner.getEnd())[not self.isTriggerOnStart()]

                # Offset by duration
                dt.copy(trigger + self.getTriggerDuration())

Component.registerComponent(definitions.cICalComponent_VALARM, VAlarm)
