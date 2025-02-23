from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from app.database.db_main import get_session
from app.database.trip_crud import *
from app.database.user_crud import get_user_by_email
from app.models import Trip_Create, Trip_Read
from sqlalchemy.exc import NoResultFound
from app.util.auth import get_current_user

admin_user_email = "adminUser@gmail.com"

router = APIRouter()

@router.post("/trip", status_code=status.HTTP_201_CREATED, response_model=Trip_Read)
def create_trip(trip: Trip_Create, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        current_user_email = current_user.email
        current_user_details = get_user_by_email(current_user_email, session)
        result = create_trip_in_db(trip, current_user_details, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/trip/all", status_code=status.HTTP_200_OK, response_model=List[Trip_Read])
def get_all_trips(offset: int = Query(ge=0), limit: int = Query(gt=0), session: Session = Depends(get_session)):
    try:
        result = get_all_trips_from_db(offset, limit, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.get("/trip/{trip_id}", status_code=status.HTTP_200_OK, response_model=Trip_Read)
def get_trip_by_id(trip_id: int, session: Session = Depends(get_session)):
    try:
        result = get_trip_by_id_from_db(trip_id, session) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.get("/trip", status_code=status.HTTP_200_OK, response_model=List[Trip_Read])
def get_filtered_trips_based_on_dates_and_title_for_user(trips_created_by_user_id: Optional[int] = Query(None), start_after: Optional[date] = Query(None), start_before: Optional[date] = Query(None), end_after: Optional[date] = Query(None), end_before: Optional[date] = Query(None), title: Optional[str] = Query(None),  current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    result = []
    if title:
        title = title.lower().strip()
    else:
        title = ""

    if not(current_user.email == admin_user_email) and trips_created_by_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges: Only admin can filter trips based on user")

    if not trips_created_by_user_id:
        trips_created_by_user_id = current_user.id

    try:
        if start_after and start_before and end_after and end_before:
            result = get_user_trips_starting_within_daterange_and_ending_within_daterange(trips_created_by_user_id, start_after, start_before, end_after, end_before, title, session)
        elif start_after and start_before and end_after:
            result = get_user_trips_starting_within_daterange_and_ending_after_specified_date(trips_created_by_user_id, start_after, start_before, end_after, title, session)
        elif start_after and start_before and end_before:
            result = get_user_trips_starting_within_daterange_and_ending_before_specified_date(trips_created_by_user_id, start_after, start_before, end_before, title, session)
        elif start_after and end_after and end_before:
            result = get_user_trips_ending_within_daterange_and_starting_after_specified_date(trips_created_by_user_id, start_after, end_after, end_before, title, session)
        elif start_before and end_after and end_before:
            result = get_user_trips_ending_within_daterange_and_starting_before_specified_date(trips_created_by_user_id, start_before, end_after, end_before, title, session)
        elif start_after and start_before:
            result = get_user_trips_starting_between_specified_dates(trips_created_by_user_id, start_after, start_before, title, session)
        elif start_after and end_after:
            result = get_user_trips_starting_after_and_ending_after_specified_dates(trips_created_by_user_id, start_after, end_after, title, session)
        elif start_after and end_before:
            result = get_user_trips_starting_and_ending_within_specified_daterange(trips_created_by_user_id, start_after, end_before, title, session)
        elif start_before and end_after:
            result = get_user_trips_starting_before_and_ending_after_specified_dates(trips_created_by_user_id, start_before, end_after, title, session)
        elif start_before and end_before:
            result = get_user_trips_starting_before_and_ending_before_specified_dates(trips_created_by_user_id, start_before, end_before, title, session)
        elif end_after and end_before:
            result = get_user_trips_ending_between_specified_dates(trips_created_by_user_id, end_after, end_before, title, session)
        elif start_after:
            result = get_user_trips_starting_after_specified_date(trips_created_by_user_id, start_after, title, session)
        elif start_before:
            result = get_user_trips_starting_before_specified_date(trips_created_by_user_id, start_before, title, session)
        elif end_after:
            result = get_user_trips_ending_after_specified_date(trips_created_by_user_id, end_after, title, session)
        elif end_before:
            result = get_user_trips_ending_before_specified_date(trips_created_by_user_id, end_before, title, session)
        elif trips_created_by_user_id:
            result = filter_trip_by_user(trips_created_by_user_id, title, session) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    
    return result

@router.put("/trip/traveller/add", status_code=status.HTTP_200_OK)
def add_traveller_to_the_trip(trip_id: int, user_id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
        user = get_user_by_id_from_db(user_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not trip and not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip and User both not found")
    elif not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip not found")
    elif not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")

    if not trip.created_by_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

    try:
        result = add_traveller_to_the_trip_in_db(trip_id, user_id, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.put("/trip/update/dates", status_code=status.HTTP_200_OK)
def update_trip_startdate_and_enddate(trip_id: int, start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    if not (start_date or end_date):
            raise HTTPException(status_code=status.HTTP_200_OK, detail=f"start date or end date not passed")
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip not found")

    if not trip.created_by_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

    try:
        result = update_trip_startdate_and_enddate_in_db(trip_id, start_date, end_date, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.put("/trip/update/title", status_code=status.HTTP_200_OK)
def update_trip_title(trip_id: int, title: str, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip not found")

    if not trip.created_by_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

    try:
        result = update_trip_title_in_db(trip_id, title, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.delete("/trip/remove", status_code=status.HTTP_200_OK)
def delete_trip(trip_id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
        if not trip.created_by_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

        result = remove_trip_from_db(trip_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.delete("/trip/traveller/remove", status_code=status.HTTP_200_OK)
def remove_traveller_from_the_trip(trip_id: int, user_id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip not found")

    if not trip.created_by_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

    try:
        result = remove_traveller_from_the_trip_in_db(trip_id, user_id, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
