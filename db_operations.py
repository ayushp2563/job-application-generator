from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import List, Optional, Dict, Any

from database import User, Job, GeneratedDocument, PortfolioItem

# User operations
def create_user(db: Session, email: str, hashed_password: str):
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Job operations
def create_job(db: Session, user_id: int, job_data: Dict[str, Any]):
    # Convert skills list to comma-separated string if it's a list
    skills = job_data.get("skills", [])
    if isinstance(skills, list):
        skills = ", ".join(skills)
    
    db_job = Job(
        user_id=user_id,
        url=job_data.get("url", ""),
        company=job_data.get("company", "Unknown Company"),
        role=job_data.get("role", "Unknown Role"),
        description=job_data.get("description", ""),
        experience=job_data.get("experience", ""),
        skills=skills,
        date_saved=datetime.utcnow()
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_user_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Job).filter(Job.user_id == user_id).offset(skip).limit(limit).all()


def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def delete_job(db: Session, job_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        db.delete(job)
        db.commit()
        return True
    return False


# Generated document operations
def create_generated_document(db: Session, job_id: int, document_type: str, content: str):
    db_document = GeneratedDocument(
        job_id=job_id,
        document_type=document_type,
        content=content,
        created_at=datetime.utcnow()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_documents_by_job_id(db: Session, job_id: int):
    return db.query(GeneratedDocument).filter(GeneratedDocument.job_id == job_id).all()


def get_document_by_id(db: Session, document_id: int):
    return db.query(GeneratedDocument).filter(GeneratedDocument.id == document_id).first()


# Portfolio operations
def create_portfolio_item(db: Session, user_id: int, tech_stack: str, link: str):
    db_item = PortfolioItem(
        user_id=user_id,
        tech_stack=tech_stack,
        link=link,
        created_at=datetime.utcnow()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_portfolio(db: Session, user_id: int):
    return db.query(PortfolioItem).filter(PortfolioItem.user_id == user_id).all()


def delete_portfolio_item(db: Session, item_id: int):
    item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False


def query_portfolio_by_skills(db: Session, user_id: int, skills: List[str], limit: int = 3):
    """
    Find portfolio items that match the given skills
    Using simple string matching
    """
    portfolio_items = db.query(PortfolioItem).filter(PortfolioItem.user_id == user_id).all()
    
    # Convert skills to lowercase for case-insensitive matching
    lowercase_skills = [skill.lower() for skill in skills if isinstance(skill, str)]
    
    # Calculate relevance score for each portfolio item
    scored_items = []
    for item in portfolio_items:
        score = 0
        tech_stack_lower = item.tech_stack.lower()
        
        for skill in lowercase_skills:
            if skill in tech_stack_lower:
                score += 1
                
        if score > 0:
            scored_items.append((item, score))
    
    # Sort by relevance score (highest first)
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top N most relevant items
    return [item for item, score in scored_items[:limit]]