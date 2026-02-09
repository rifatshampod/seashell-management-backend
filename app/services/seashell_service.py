"""
Seashell Service - Business logic layer for seashell operations.
Handles CRUD operations and filtering for seashell collection management.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import Seashell
from app.schemas.seashell import SeashellCreate, SeashellUpdate


class SeashellServiceError(Exception):
    """Base exception for seashell service errors."""
    pass


class SeashellNotFoundError(SeashellServiceError):
    """Raised when a seashell is not found."""
    pass


class SeashellService:
    """Service class for seashell-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_seashell(self, seashell_data: SeashellCreate, added_by_id: Optional[UUID] = None) -> Seashell:
        """
        Create a new seashell entry.
        
        Args:
            seashell_data: Seashell data containing name, species, and optional fields.
            added_by_id: UUID of the user who is adding this seashell.
            
        Returns:
            The created Seashell object.
        """
        seashell = Seashell(
            name=seashell_data.name,
            species=seashell_data.species,
            description=seashell_data.description,
            color=seashell_data.color,
            size_mm=seashell_data.size_mm,
            found_on=seashell_data.found_on,
            found_at=seashell_data.found_at,
            storage_location=seashell_data.storage_location,
            condition=seashell_data.condition,
            notes=seashell_data.notes,
            image_url=seashell_data.image_url,
            added_by_id=added_by_id,
        )

        self.db.add(seashell)
        self.db.commit()
        self.db.refresh(seashell)
        return seashell

    def get_seashell_by_id(self, seashell_id: UUID) -> Seashell:
        """
        Get a seashell by its ID.
        
        Args:
            seashell_id: The UUID of the seashell.
            
        Returns:
            The Seashell object.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
        """
        seashell = self.db.query(Seashell).filter(Seashell.id == seashell_id).first()
        if not seashell:
            raise SeashellNotFoundError(f"Seashell with id {seashell_id} not found")
        return seashell

    def get_all_seashells(
        self,
        skip: int = 0,
        limit: int = 100,
        species: Optional[str] = None,
        color: Optional[str] = None,
        condition: Optional[str] = None,
        storage_location: Optional[str] = None,
        min_size_mm: Optional[int] = None,
        max_size_mm: Optional[int] = None,
        found_after: Optional[date] = None,
        found_before: Optional[date] = None,
        search: Optional[str] = None,
    ) -> List[Seashell]:
        """
        Get all seashells with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.
            species: Filter by species (exact match).
            color: Filter by color (exact match).
            condition: Filter by condition (exact match).
            storage_location: Filter by storage location (exact match).
            min_size_mm: Filter by minimum size in mm.
            max_size_mm: Filter by maximum size in mm.
            found_after: Filter by found_on date after this date.
            found_before: Filter by found_on date before this date.
            search: Search term for name, species, or description.
            
        Returns:
            List of Seashell objects matching the criteria.
        """
        query = self.db.query(Seashell)

        # Apply filters
        if species:
            query = query.filter(Seashell.species == species)
        if color:
            query = query.filter(Seashell.color == color)
        if condition:
            query = query.filter(Seashell.condition == condition)
        if storage_location:
            query = query.filter(Seashell.storage_location == storage_location)
        if min_size_mm is not None:
            query = query.filter(Seashell.size_mm >= min_size_mm)
        if max_size_mm is not None:
            query = query.filter(Seashell.size_mm <= max_size_mm)
        if found_after:
            query = query.filter(Seashell.found_on >= found_after)
        if found_before:
            query = query.filter(Seashell.found_on <= found_before)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Seashell.name.ilike(search_term),
                    Seashell.species.ilike(search_term),
                    Seashell.description.ilike(search_term),
                )
            )

        # Apply pagination and return results
        return query.offset(skip).limit(limit).all()

    def count_seashells(
        self,
        species: Optional[str] = None,
        color: Optional[str] = None,
        condition: Optional[str] = None,
        storage_location: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count seashells with optional filtering.
        
        Args:
            species: Filter by species.
            color: Filter by color.
            condition: Filter by condition.
            storage_location: Filter by storage location.
            search: Search term for name, species, or description.
            
        Returns:
            Total count of matching seashells.
        """
        query = self.db.query(Seashell)

        if species:
            query = query.filter(Seashell.species == species)
        if color:
            query = query.filter(Seashell.color == color)
        if condition:
            query = query.filter(Seashell.condition == condition)
        if storage_location:
            query = query.filter(Seashell.storage_location == storage_location)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Seashell.name.ilike(search_term),
                    Seashell.species.ilike(search_term),
                    Seashell.description.ilike(search_term),
                )
            )

        return query.count()

    def update_seashell(self, seashell_id: UUID, update_data: SeashellUpdate) -> Seashell:
        """
        Update a seashell's information.
        
        Args:
            seashell_id: The UUID of the seashell to update.
            update_data: The fields to update.
            
        Returns:
            The updated Seashell object.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
        """
        seashell = self.get_seashell_by_id(seashell_id)

        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(seashell, field, value)

        self.db.commit()
        self.db.refresh(seashell)
        return seashell

    def delete_seashell(self, seashell_id: UUID) -> None:
        """
        Delete a seashell from the collection.
        
        Args:
            seashell_id: The UUID of the seashell to delete.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
        """
        seashell = self.get_seashell_by_id(seashell_id)
        self.db.delete(seashell)
        self.db.commit()

    def get_unique_species(self) -> List[str]:
        """
        Get a list of all unique species in the collection.
        
        Returns:
            List of unique species names.
        """
        results = self.db.query(Seashell.species).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_unique_colors(self) -> List[str]:
        """
        Get a list of all unique colors in the collection.
        
        Returns:
            List of unique color names.
        """
        results = self.db.query(Seashell.color).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_unique_storage_locations(self) -> List[str]:
        """
        Get a list of all unique storage locations in the collection.
        
        Returns:
            List of unique storage locations.
        """
        results = self.db.query(Seashell.storage_location).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_unique_conditions(self) -> List[str]:
        """
        Get a list of all unique conditions in the collection.
        
        Returns:
            List of unique conditions.
        """
        results = self.db.query(Seashell.condition).distinct().all()
        return [r[0] for r in results if r[0]]
