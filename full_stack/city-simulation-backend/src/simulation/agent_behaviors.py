import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class AgentBehavior:
    """Base class for agent behaviors"""
    
    def __init__(self, role: str):
        self.role = role
        self.default_schedule = self._get_default_schedule()
        self.activity_preferences = self._get_activity_preferences()
    
    def update(self, agent_data: Dict, current_time: datetime) -> Optional[Dict]:
        """Update agent behavior and return next action"""
        # Get current hour for schedule-based decisions
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Check if agent is currently in an activity
        if self._is_in_activity(agent_data, current_time):
            return None  # Continue current activity
        
        # Get scheduled activity for current time
        scheduled_activity = self._get_scheduled_activity(agent_data, current_hour, current_minute)
        
        if scheduled_activity:
            return self._create_activity_action(scheduled_activity, agent_data)
        
        # Default behavior when no specific schedule
        return self._get_default_action(agent_data, current_time)
    
    def _is_in_activity(self, agent_data: Dict, current_time: datetime) -> bool:
        """Check if agent is currently engaged in an activity"""
        if agent_data.get('status') == 'idle':
            return False
        
        activity_start = agent_data.get('activity_start_time')
        activity_duration = agent_data.get('activity_duration', 0)
        
        if activity_start and activity_duration:
            start_time = datetime.fromisoformat(activity_start.replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=activity_duration)
            return current_time < end_time
        
        return False
    
    def _get_scheduled_activity(self, agent_data: Dict, hour: int, minute: int) -> Optional[Dict]:
        """Get scheduled activity for current time"""
        schedule = agent_data.get('schedule', {})
        
        # Check hourly schedule
        hour_key = f"{hour:02d}:00"
        if hour_key in schedule:
            return schedule[hour_key]
        
        # Check for time ranges
        for time_range, activity in schedule.items():
            if '-' in time_range:
                start_str, end_str = time_range.split('-')
                start_hour = int(start_str.split(':')[0])
                end_hour = int(end_str.split(':')[0])
                
                if start_hour <= hour < end_hour:
                    return activity
        
        return None
    
    def _create_activity_action(self, activity: Dict, agent_data: Dict) -> Dict:
        """Create an action for a scheduled activity"""
        activity_type = activity.get('type', 'work')
        location_id = activity.get('location_id')
        duration = activity.get('duration', 60)
        
        if location_id and location_id != agent_data.get('current_location_id'):
            # Need to move to location first
            return {
                'type': 'move',
                'target_location_id': location_id,
                'transport_mode': activity.get('transport_mode', 'walking')
            }
        else:
            # Start activity at current location
            return {
                'type': 'activity',
                'activity_type': activity_type,
                'duration': duration
            }
    
    def _get_default_action(self, agent_data: Dict, current_time: datetime) -> Optional[Dict]:
        """Get default action when no schedule is defined"""
        # Random behavior based on role
        if random.random() < 0.1:  # 10% chance of random movement
            return self._get_random_movement_action(agent_data)
        
        return None  # Stay idle
    
    def _get_random_movement_action(self, agent_data: Dict) -> Dict:
        """Generate a random movement action"""
        # Simple random movement within a small area
        current_x = agent_data.get('x', 0)
        current_y = agent_data.get('y', 0)
        
        # Move within 1km radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.1, 1.0)
        
        target_x = current_x + distance * math.cos(angle)
        target_y = current_y + distance * math.sin(angle)
        
        return {
            'type': 'move',
            'target_x': target_x,
            'target_y': target_y,
            'transport_mode': 'walking'
        }
    
    def _get_default_schedule(self) -> Dict:
        """Get default schedule for this role"""
        return {}
    
    def _get_activity_preferences(self) -> Dict:
        """Get activity preferences for this role"""
        return {}

class StudentBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('student')
    
    def _get_default_schedule(self) -> Dict:
        return {
            '07:00-08:00': {'type': 'breakfast', 'duration': 30},
            '08:00-12:00': {'type': 'attending_class', 'duration': 240},
            '12:00-13:00': {'type': 'lunch', 'duration': 60},
            '13:00-17:00': {'type': 'studying', 'duration': 240},
            '17:00-18:00': {'type': 'recreation', 'duration': 60},
            '18:00-19:00': {'type': 'dinner', 'duration': 60},
            '19:00-22:00': {'type': 'homework', 'duration': 180},
            '22:00-07:00': {'type': 'sleeping', 'duration': 540}
        }

class SoftwareEngineerBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('software_engineer')
    
    def _get_default_schedule(self) -> Dict:
        return {
            '07:00-08:00': {'type': 'breakfast', 'duration': 30},
            '08:00-09:00': {'type': 'commuting', 'duration': 60, 'transport_mode': 'car'},
            '09:00-12:00': {'type': 'coding', 'duration': 180},
            '12:00-13:00': {'type': 'lunch', 'duration': 60},
            '13:00-17:00': {'type': 'meetings', 'duration': 240},
            '17:00-18:00': {'type': 'commuting_home', 'duration': 60, 'transport_mode': 'car'},
            '18:00-19:00': {'type': 'dinner', 'duration': 60},
            '19:00-22:00': {'type': 'personal_time', 'duration': 180},
            '22:00-07:00': {'type': 'sleeping', 'duration': 540}
        }

class TeacherBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('teacher')
    
    def _get_default_schedule(self) -> Dict:
        return {
            '07:00-08:00': {'type': 'breakfast', 'duration': 30},
            '08:00-08:30': {'type': 'commuting', 'duration': 30, 'transport_mode': 'car'},
            '08:30-12:00': {'type': 'teaching', 'duration': 210},
            '12:00-13:00': {'type': 'lunch', 'duration': 60},
            '13:00-16:00': {'type': 'grading', 'duration': 180},
            '16:00-16:30': {'type': 'commuting_home', 'duration': 30, 'transport_mode': 'car'},
            '16:30-18:00': {'type': 'lesson_planning', 'duration': 90},
            '18:00-19:00': {'type': 'dinner', 'duration': 60},
            '19:00-22:00': {'type': 'personal_time', 'duration': 180},
            '22:00-07:00': {'type': 'sleeping', 'duration': 540}
        }

class RestaurantStaffBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('restaurant_staff')
    
    def _get_default_schedule(self) -> Dict:
        return {
            '09:00-10:00': {'type': 'preparation', 'duration': 60},
            '10:00-14:00': {'type': 'serving_customers', 'duration': 240},
            '14:00-15:00': {'type': 'break', 'duration': 60},
            '15:00-22:00': {'type': 'serving_customers', 'duration': 420},
            '22:00-23:00': {'type': 'cleanup', 'duration': 60}
        }

class DeliveryPersonnelBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('delivery_personnel')
    
    def _get_default_schedule(self) -> Dict:
        return {
            '08:00-12:00': {'type': 'delivering', 'duration': 240, 'transport_mode': 'car'},
            '12:00-13:00': {'type': 'lunch', 'duration': 60},
            '13:00-18:00': {'type': 'delivering', 'duration': 300, 'transport_mode': 'car'},
            '18:00-19:00': {'type': 'vehicle_maintenance', 'duration': 60}
        }
    
    def _get_default_action(self, agent_data: Dict, current_time: datetime) -> Optional[Dict]:
        """Delivery personnel move more frequently"""
        if random.random() < 0.3:  # 30% chance of movement
            return self._get_delivery_movement_action(agent_data)
        return super()._get_default_action(agent_data, current_time)
    
    def _get_delivery_movement_action(self, agent_data: Dict) -> Dict:
        """Generate delivery-specific movement"""
        # Delivery personnel move in larger areas
        current_x = agent_data.get('x', 0)
        current_y = agent_data.get('y', 0)
        
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(1.0, 5.0)  # Larger delivery radius
        
        target_x = current_x + distance * math.cos(angle)
        target_y = current_y + distance * math.sin(angle)
        
        return {
            'type': 'move',
            'target_x': target_x,
            'target_y': target_y,
            'transport_mode': 'car'
        }

class CitizenBehavior(AgentBehavior):
    def __init__(self):
        super().__init__('citizen')
    
    def _get_default_schedule(self) -> Dict:
        # Citizens have more varied schedules
        schedules = [
            {  # Working citizen
                '08:00-09:00': {'type': 'commuting', 'duration': 60},
                '09:00-17:00': {'type': 'working', 'duration': 480},
                '17:00-18:00': {'type': 'commuting_home', 'duration': 60},
                '18:00-19:00': {'type': 'dinner', 'duration': 60},
                '19:00-22:00': {'type': 'leisure', 'duration': 180}
            },
            {  # Retired citizen
                '09:00-10:00': {'type': 'breakfast', 'duration': 60},
                '10:00-12:00': {'type': 'shopping', 'duration': 120},
                '12:00-13:00': {'type': 'lunch', 'duration': 60},
                '13:00-16:00': {'type': 'socializing', 'duration': 180},
                '16:00-18:00': {'type': 'walking', 'duration': 120},
                '18:00-19:00': {'type': 'dinner', 'duration': 60}
            }
        ]
        return random.choice(schedules)

class AgentBehaviorManager:
    """Manages behaviors for different agent types"""
    
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine
        self.behaviors = {
            'student': StudentBehavior(),
            'software_engineer': SoftwareEngineerBehavior(),
            'teacher': TeacherBehavior(),
            'restaurant_staff': RestaurantStaffBehavior(),
            'restaurant_customer': CitizenBehavior(),  # Use citizen behavior
            'grocery_worker': RestaurantStaffBehavior(),  # Similar to restaurant staff
            'grocery_shopper': CitizenBehavior(),
            'delivery_personnel': DeliveryPersonnelBehavior(),
            'citizen': CitizenBehavior(),
            'police_officer': CitizenBehavior(),  # Can be enhanced later
            'firefighter': CitizenBehavior(),
            'doctor': TeacherBehavior(),  # Similar schedule to teacher
            'nurse': TeacherBehavior(),
            'bus_driver': DeliveryPersonnelBehavior(),  # Similar to delivery
            'taxi_driver': DeliveryPersonnelBehavior()
        }
    
    def get_behavior(self, role: str) -> AgentBehavior:
        """Get behavior instance for a specific role"""
        return self.behaviors.get(role, CitizenBehavior())
    
    def add_behavior(self, role: str, behavior: AgentBehavior):
        """Add a custom behavior for a role"""
        self.behaviors[role] = behavior
    
    def get_available_roles(self) -> List[str]:
        """Get list of available agent roles"""
        return list(self.behaviors.keys())

