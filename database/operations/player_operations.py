from database.models import Player, PlayerSkill, RecipeSkillRequirement, TradeSkill, Server

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

def get_player_skills(session, player_id):
    """
    Retrieve the skills and skill levels of a player.
    
    Args:
        session: The SQLAlchemy session object.
        player_id: The ID of the player for whom to fetch the skills.
    
    Returns:
        A list of dictionaries containing skill names and their corresponding levels for the player.
    """
    # Join the tables to get the required data
    results = session.query(PlayerSkill.skill_level, TradeSkill.skill_name).join(
        TradeSkill, PlayerSkill.skill_id == TradeSkill.skill_id
    ).filter(PlayerSkill.player_id == player_id).all()

    skills_data = [{"skill_name": skill_name, "skill_level": skill_level} for skill_level, skill_name in results]
    
    return skills_data


def can_craft_recipe(session, player_id, recipe_id):
    # Fetch the player's skills and skill levels
    player_skills = {ps.skill_id: ps.skill_level for ps in session.query(PlayerSkill).filter(PlayerSkill.player_id == player_id)}

    # Fetch the skill requirements for the recipe
    recipe_skill_requirements = session.query(RecipeSkillRequirement).filter(RecipeSkillRequirement.recipe_id == recipe_id)

    # Iterate through each skill requirement to check if the player has the required skill level
    for req in recipe_skill_requirements:
        player_skill_level = player_skills.get(req.skill_id, 0)
        if player_skill_level < req.level_required:
            return False  # Player does not meet the skill level requirement for crafting

    # If all requirements are met
    return True


def delete_player(session, player_id):
    """
    Delete a player and their associated skills from the database.
    
    Args:
        session: The SQLAlchemy session object.
        player_id: The ID of the player to delete.
    """
    # First, delete the player's associated skills
    session.query(PlayerSkill).filter(PlayerSkill.player_id == player_id).delete()

    # Then, delete the player
    player = session.query(Player).filter(Player.player_id == player_id).first()
    if player:
        session.delete(player)

    # Commit the session to finalize the deletion
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