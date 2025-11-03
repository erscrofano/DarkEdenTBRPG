"""Enemy model class"""


class Enemy:
    def __init__(self, name, hp, attack, defense, exp_reward, gold_reward, drops=None):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.drops = drops if drops else []
    
    def take_damage(self, damage):
        """
        Apply damage to enemy, reducing by defense.
        
        DAMAGE FLOW DOCUMENTATION:
        - This is the SINGLE point where enemy defense is applied.
        - Upstream code should pass RAW damage (before defense).
        - Defense reduces damage, minimum 1 damage always dealt.
        - Returns actual damage taken for display purposes.
        """
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage
    
    def is_alive(self):
        return self.hp > 0
    
    def get_stats(self):
        return f"{self.name} - HP: {self.hp}/{self.max_hp}"

