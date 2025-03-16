class MonitorState:
    def __init__(self):
        self.last_height = 0
        self.missed_since_last_alert = 0
        self.total_missed = 0
        self.total_blocks = 0
        self.avg_block_time = 0
        self.active = False
        self.voting_power = None
        self.total_voting_power = None
        self.rank = None
        self.jailed = False
        self.delegator_count = None
        self.uptime = None

state = MonitorState()