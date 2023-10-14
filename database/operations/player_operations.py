from database.models import Player, PlayerSkill, TradeSkill, Server

def add_player(session, player_data):
    # Retrieve the server
    server = session.query(Server).filter(Server.server_name == player_data["server_name"]).first()
    
    # If the server doesn't exist, we should handle this case, either by skipping or raising an error
    if not server:
        raise ValueError(f"Server '{player_data['server_name']}' not found!")

    # Create a Player instance
    player = Player(player_name=player_data["player_name"], server_id=server.server_id)

    # Add the player to the session (but don't commit yet)
    session.add(player)
    
    # After adding the player to the session, we need to flush to ensure it's temporarily saved 
    # so we can get its ID (needed for associating skills)
    session.flush()

    # Associate the player with the skills
    for skill_data in player_data["skills"]:
        # Retrieve the TradeSkill entry by skill name
        trade_skill = session.query(TradeSkill).filter(TradeSkill.skill_name == skill_data["skill_name"]).first()

        # If the skill doesn't exist, we should handle this case, either by skipping or raising an error
        if not trade_skill:
            raise ValueError(f"Skill '{skill_data['skill_name']}' not found!")

        # Create PlayerSkill entry
        player_skill = PlayerSkill(player_id=player.player_id, skill_id=trade_skill.skill_id, skill_level=skill_data["skill_level"])
        
        # Add to the session
        session.add(player_skill)

    # Commit the session to save everything
    session.commit()


def update_player(session, player_id, new_data):
    # Query for the existing player entry
    player = session.query(Player).filter(Player.player_id == player_id).first()
    
    # Update the top-level player attributes
    for key, value in new_data.items():
        if key != "skills":
            setattr(player, key, value)

    # Handle the skills if present in new_data
    if "skills" in new_data:
        # Remove the current skills of the player
        session.query(PlayerSkill).filter(PlayerSkill.player_id == player_id).delete()

        # Add the new skills from new_data
        for skill_data in new_data["skills"]:
            trade_skill = session.query(TradeSkill).filter(TradeSkill.skill_name == skill_data["skill_name"]).first()
            
            # Check if the skill exists
            if trade_skill:
                player_skill = PlayerSkill(player_id=player.player_id, skill_id=trade_skill.skill_id, skill_level=skill_data["skill_level"])
                session.add(player_skill)
            else:
                # Handle case where the skill doesn't exist, e.g., raise an error or log a message
                pass

    # Commit the session
    session.commit()


def get_player_by_id(session, player_id):
    # Query for the player with the specified ID
    player = session.query(Player).filter(Player.player_id == player_id).first()
    
    # Convert the result to a dictionary (excluding SQLAlchemy's internal attributes)
    if player:
        return {key: value for key, value in player.__dict__.items() if not key.startswith('_')}
    return None

def get_player_by_name(session, player_name):
    # Query for the player with the specified name
    player = session.query(Player).filter(Player.player_name == player_name).first()

    # Convert the result to a dictionary (excluding SQLAlchemy's internal attributes)
    if player:
        return {key: value for key, value in player.__dict__.items() if not key.startswith('_')}
    return None