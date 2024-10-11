from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# Enums
class StatusEnum(str, Enum):
    alive = "alive"
    dead = "dead"

# Basic Models
class Coordinate(BaseModel):
    x: int
    y: int

class Vector(BaseModel):
    x: float
    y: float

# Request Models
class CommandTransport(BaseModel):
    id: str
    acceleration: Optional[Vector]
    activateShield: Optional[bool]
    attack: Optional[Coordinate]

class CommandPlayer(BaseModel):
    transports: List[CommandTransport]

# Response Models
class Anomaly(BaseModel):
    x: int
    y: int
    effectiveRadius: Optional[float]
    id: Optional[str]
    radius: Optional[float]
    strength: Optional[float]
    velocity: Optional[Vector]

class Bounty(BaseModel):
    x: int
    y: int
    points: Optional[int]
    radius: Optional[int]

class Enemy(BaseModel):
    x: int
    y: int
    health: Optional[int]
    killBounty: Optional[int]
    shieldLeftMs: Optional[int]
    status: Optional[StatusEnum]
    velocity: Optional[Vector]

class ViewTransport(BaseModel):
    x: int
    y: int
    id: Optional[str]
    health: Optional[int]
    status: Optional[StatusEnum]
    velocity: Optional[Vector]
    anomalyAcceleration: Optional[Vector]
    selfAcceleration: Optional[Vector]
    shieldCooldownMs: Optional[int]
    shieldLeftMs: Optional[int]
    attackCooldownMs: Optional[int]
    deathCount: Optional[int]

class ViewPlayer(BaseModel):
    anomalies: Optional[List[Anomaly]]
    attackCooldownMs: Optional[int]
    attackDamage: Optional[int]
    attackExplosionRadius: Optional[float]
    attackRange: Optional[float]
    bounties: Optional[List[Bounty]]
    enemies: Optional[List[Enemy]]
    mapSize: Optional[Coordinate]
    maxAccel: Optional[float]
    maxSpeed: Optional[float]
    name: Optional[str]
    points: Optional[int]
    reviveTimeoutSec: Optional[int]
    shieldCooldownMs: Optional[int]
    shieldTimeMs: Optional[int]
    transportRadius: Optional[int]
    transports: Optional[List[ViewTransport]]
    wantedList: Optional[List[Enemy]]

class Round(BaseModel):
    duration: Optional[int]
    endAt: Optional[str]
    name: Optional[str]
    repeat: Optional[int]
    startAt: Optional[str]
    status: Optional[str]

class RoundList(BaseModel):
    gameName: Optional[str]
    now: Optional[str]
    rounds: Optional[List[Round]]

# Error Models
class PubErr(BaseModel):
    errCode: int
    error: str

class ErrNotAuthorized(BaseModel):
    errCode: int
    error: str

class ErrForbidden(BaseModel):
    errCode: int
    error: str

class ErrNotFound(BaseModel):
    errCode: int
    error: str

class ErrTooManyUserRequests(BaseModel):
    errCode: int
    error: str
