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

#image upload delete
from app.core.file_upload import delete_seashell_images


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

    async def create_seashell_with_image(
        self,
        seashell_data: SeashellCreate,
        added_by_id: Optional[UUID] = None,
        file: Optional["UploadFile"] = None,
    ) -> Seashell:
        """
        Create a new seashell entry with optional image upload.
        
        Handles the full workflow: creates the seashell record, uploads the image
        if provided, and updates the image URL in the database. If image upload
        fails, the seashell record is rolled back (deleted).
        
        Args:
            seashell_data: Seashell data containing name, species, and optional fields.
            added_by_id: UUID of the user who is adding this seashell.
            file: Optional uploaded image file.
            
        Returns:
            The created Seashell object with image_url populated if image was uploaded.
            
        Raises:
            InvalidFileTypeError: If file type is not allowed.
            FileTooLargeError: If file exceeds size limit.
            Exception: If image upload fails for any other reason.
        """
        from app.core.file_upload import save_upload_file
        
        # Step 1: Create the seashell record
        seashell = self.create_seashell(seashell_data, added_by_id=added_by_id)
        
        # Step 2: Upload image if provided
        if file:
            try:
                image_url = await save_upload_file(file, str(seashell.id))
                seashell = self.update_image_url(seashell.id, image_url)
            except Exception:
                # Rollback: delete the seashell if image upload fails
                self.delete_seashell(seashell.id)
                raise
        
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

    async def update_seashell_with_image(
        self,
        seashell_id: UUID,
        update_data: SeashellUpdate,
        file: Optional["UploadFile"] = None,
    ) -> Seashell:
        """
        Update a seashell's information with optional image upload.
        
        Handles the full workflow: updates the seashell record, uploads the image
        if provided, and updates the image URL in the database.
        
        Args:
            seashell_id: The UUID of the seashell to update.
            update_data: The fields to update.
            file: Optional uploaded image file.
            
        Returns:
            The updated Seashell object with image_url populated if image was uploaded.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
            InvalidFileTypeError: If file type is not allowed.
            FileTooLargeError: If file exceeds size limit.
            Exception: If image upload fails for any other reason.
        """
        from app.core.file_upload import save_upload_file, delete_image_file
        
        # Step 1: Update the seashell record
        seashell = self.update_seashell(seashell_id, update_data)
        
        # Step 2: Upload new image if provided
        if file:
            # Delete old image if exists
            if seashell.image_url:
                delete_image_file(seashell.image_url)
            
            # Upload new image
            image_url = await save_upload_file(file, str(seashell_id))
            seashell = self.update_image_url(seashell_id, image_url)
        
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
        
        # Delete associated images
        delete_seashell_images(str(seashell_id))
        
        self.db.delete(seashell)
        self.db.commit()

    def update_image_url(self, seashell_id: UUID, image_url: str) -> "Seashell":
        """
        Update the image URL for a seashell.
        
        Args:
            seashell_id: The UUID of the seashell.
            image_url: The new image URL.
            
        Returns:
            The updated Seashell object.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
        """
        seashell = self.get_seashell_by_id(seashell_id)
        seashell.image_url = image_url
        self.db.commit()
        self.db.refresh(seashell)
        return seashell

    def delete_image(self, seashell_id: UUID) -> "Seashell":
        """
        Delete the image for a seashell.
        
        Args:
            seashell_id: The UUID of the seashell.
            
        Returns:
            The updated Seashell object.
            
        Raises:
            SeashellNotFoundError: If the seashell is not found.
        """
        from app.core.file_upload import delete_image_file
        
        seashell = self.get_seashell_by_id(seashell_id)
        
        if seashell.image_url:
            delete_image_file(seashell.image_url)
            seashell.image_url = None
            self.db.commit()
            self.db.refresh(seashell)
        
        return seashell

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

